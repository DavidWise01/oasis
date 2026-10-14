#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <sys/socket.h>
#include <unistd.h>
#include <vector>
#include <map>
using std::uint8_t;
constexpr size_t MAX_N=65536;
static uint32_t be32(const uint8_t *p){return uint32_t(p[0])<<24|uint32_t(p[1])<<16|uint32_t(p[2])<<8|uint32_t(p[3]);}
static void put32(uint8_t *p,uint32_t n){p[0]=n>>24;p[1]=n>>16;p[2]=n>>8;p[3]=n;}
static uint32_t crc32(const uint8_t *p,size_t n){uint32_t c=~0u;for(size_t i=0;i<n;i++){c^=p[i];for(int j=0;j<8;j++)c=(c>>1)^((c&1)?0xedb88320u:0);}return ~c;}
static void op(std::vector<uint32_t>& a, char c, bool inverse){
 const size_t n=a.size(); if(!n)return;
 if(c=='U'||c=='D'||c=='A'){
  int k=c=='U'?1:c=='D'?-1:2;if(inverse)k=-k;
  int v=(k%int(n)+int(n))%int(n);
  if(v)std::rotate(a.begin(),a.end()-v,a.end());
 }else if(c=='B')std::reverse(a.begin(),a.end());
 else if(c=='L'||c=='R') for(size_t i=c=='L'?0:1;i+1<n;i+=2)std::swap(a[i],a[i+1]);
}
struct Maps{std::vector<uint32_t> p,m;};
static std::map<size_t,Maps> cache;
static const Maps& maps(size_t n){
 auto it=cache.find(n);if(it!=cache.end())return it->second;
 Maps m; m.p.resize(n);m.m.resize(n);for(size_t i=0;i<n;i++){m.p[i]=i;m.m[i]=n-1-i;}
 const char* code="UUDDLRLRBASS";for(int pass=0;pass<5;pass++)for(int j=0;j<12;j++){op(m.p,code[j],false);op(m.m,code[11-j],true);}std::reverse(m.m.begin(),m.m.end());
 if(cache.size()>=16)cache.erase(cache.begin());
 return cache.emplace(n,std::move(m)).first->second;
}
static bool decode(const std::vector<uint8_t>& frame,std::vector<uint8_t>& out){
 size_t len=frame.size();if(len<16||len>16+2*MAX_N)return false;
 const uint8_t* x=frame.data();if(memcmp(x,"OBF2",4)!=0||x[4]!=1||x[5]!=1||x[6]!=0||x[7]!=0)return false;
 uint32_t n=be32(x+8);if(n>MAX_N||len!=16+2u*n||crc32(x,len-4)!=be32(x+len-4))return false;
 const Maps& pm=maps(n);out.resize(n);std::vector<uint8_t> other(n);
 for(size_t i=0;i<n;i++){out[pm.p[i]]=x[12+i];other[pm.m[i]]=x[12+n+i];}
 return out==other;
}
static std::vector<uint8_t> encode(const std::vector<uint8_t>& bytes){
 size_t n=bytes.size();const Maps& pm=maps(n);std::vector<uint8_t> out(16+2*n);
 memcpy(out.data(),"OBF2",4);out[4]=1;out[5]=1;out[6]=out[7]=0;put32(out.data()+8,n);
 for(size_t i=0;i<n;i++){out[12+i]=bytes[pm.p[i]];out[12+n+i]=bytes[pm.m[i]];}
 put32(out.data()+out.size()-4,crc32(out.data(),out.size()-4));return out;
}
static bool read_exact(int fd,void* dst,size_t n){auto* p=static_cast<uint8_t*>(dst);while(n){ssize_t got=recv(fd,p,n,0);if(got<=0)return false;p+=got;n-=size_t(got);}return true;}
static bool send_exact(int fd,const uint8_t* p,size_t n){while(n){ssize_t k=send(fd,p,n,MSG_NOSIGNAL);if(k<=0)return false;p+=k;n-=size_t(k);}return true;}
int main(int argc,char** argv){int port=argc>1?atoi(argv[1]):31022;
 int listener=socket(AF_INET,SOCK_STREAM,0);if(listener<0)return 2;int one=1;setsockopt(listener,SOL_SOCKET,SO_REUSEADDR,&one,sizeof(one));
 sockaddr_in sa{};sa.sin_family=AF_INET;sa.sin_addr.s_addr=htonl(INADDR_LOOPBACK);sa.sin_port=htons(port);
 if(bind(listener,(sockaddr*)&sa,sizeof(sa))<0||listen(listener,64)<0){perror("bind/listen");return 3;}
 std::cout<<"READY cpp "<<port<<std::endl;
 while(true){int fd=accept(listener,nullptr,nullptr);if(fd<0)continue;setsockopt(fd,IPPROTO_TCP,TCP_NODELAY,&one,sizeof(one));
 uint8_t header[4];while(read_exact(fd,header,4)){
  const uint32_t len=be32(header);
  if(len<16||len>16+2*MAX_N){uint8_t bad[5]={1,0,0,0,0};send_exact(fd,bad,5);break;}
  std::vector<uint8_t> frame(len),recovered; if(!read_exact(fd,frame.data(),len))break;
  bool pass=decode(frame,recovered);std::vector<uint8_t> payload=pass?encode(recovered):std::vector<uint8_t>();
  std::vector<uint8_t> response(5+payload.size());response[0]=pass?0:1;put32(response.data()+1,uint32_t(payload.size()));
  if(pass)memcpy(response.data()+5,payload.data(),payload.size());
  if(!send_exact(fd,response.data(),response.size()))break;
 }
 close(fd);
 }
}
