#include <array>
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <chrono>
using A=std::array<uint8_t,32>;
constexpr const char *CODE="UUDDLRLRBASS";
void op(A& a,char op,bool inv){
 if(op=='U'||op=='D'||op=='A'){int k=op=='U'?1:op=='D'?-1:2;if(inv)k=-k;k=(k%32+32)%32;std::rotate(a.begin(),a.end()-k,a.end());}
 else if(op=='L'||op=='R'){int off=op=='L'?0:1;for(int i=off;i+1<32;i+=2)std::swap(a[i],a[i+1]);}
 else if(op=='B')std::reverse(a.begin(),a.end());
}
void perm(A &a,bool inv){for(int p=0;p<5;p++)for(int s=0;s<12;s++)op(a,CODE[inv?11-s:s],inv);}
int main(int argc,char**argv){int n=argc>1?std::atoi(argv[1]):32768;if(n<=0||n%32)return 2;auto t=std::chrono::steady_clock::now();uint32_t ck=2166136261u;
 for(int first=0;first<n;first+=32){A src,pos,neg,left,right;for(int j=0;j<32;j++)src[j]=(first+j)%44;pos=src;for(int j=0;j<32;j++)neg[j]=src[31-j];perm(pos,0);perm(neg,1);left=pos;right=neg;perm(left,1);perm(right,0);
 for(int j=0;j<32;j++)if(left[j]!=src[j]||right[31-j]!=src[j])return 3;
 for(auto x:pos)ck=(ck^x)*16777619u;for(auto x:neg)ck=(ck^x)*16777619u;}
 printf("{\"runtime\":\"cpp\",\"tokens\":%d,\"checksum\":%u,\"elapsed_s\":%.9f}\n",n,ck,std::chrono::duration<double>(std::chrono::steady_clock::now()-t).count());
}
