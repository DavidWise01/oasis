/* OASIS OBF2 v2.3: freestanding C-to-WASM codec, frozen v0.7 permutation,
 * no syscalls, no heap, bounded linear memory, no crypto/authentication. */
#include <stdint.h>
#define MAX_N 65536u
#define HEAD 12u
#define OVER 16u
#define MAX_WIRE (OVER+2u*MAX_N)
#define EXPORT(name) __attribute__((export_name(name)))
static uint8_t input[MAX_N];
static uint8_t frame[MAX_WIRE];
static uint8_t recovered[MAX_N];
static uint32_t plus[MAX_N],minus[MAX_N],scratch[MAX_N];
static uint32_t last_n=0xffffffffu;
static uint32_t crc_table[256];
static int crc_initialized=0;
static const char program[13]="UUDDLRLRBASS";
EXPORT("input_ptr") uint32_t input_ptr(void){return (uint32_t)(uintptr_t)input;}
EXPORT("frame_ptr") uint32_t frame_ptr(void){return (uint32_t)(uintptr_t)frame;}
EXPORT("recovered_ptr") uint32_t recovered_ptr(void){return (uint32_t)(uintptr_t)recovered;}
EXPORT("max_bytes") uint32_t max_bytes(void){return MAX_N;}
static void op(uint32_t *a,uint32_t n,char c,int inverse){
 if(!n)return;
 if(c=='U'||c=='D'||c=='A'){
  int32_t k=c=='U'?1:c=='D'?-1:2;if(inverse)k=-k;
  k%= (int32_t)n;if(k<0)k+=(int32_t)n;
  for(uint32_t i=0;i<n;i++)scratch[(i+(uint32_t)k)%n]=a[i];
  for(uint32_t i=0;i<n;i++)a[i]=scratch[i];
 }else if(c=='B'){
  for(uint32_t i=0;i<n/2;i++){uint32_t t=a[i];a[i]=a[n-1-i];a[n-1-i]=t;}
 }else if(c=='L'||c=='R'){
  for(uint32_t i=c=='L'?0:1;i+1<n;i+=2){uint32_t t=a[i];a[i]=a[i+1];a[i+1]=t;}
 }
}
static void maps(uint32_t n){
 if(last_n==n)return;
 for(uint32_t i=0;i<n;i++){plus[i]=i;minus[i]=n-1-i;}
 for(uint32_t pass=0;pass<5;pass++)for(uint32_t j=0;j<12;j++)op(plus,n,program[j],0);
 for(uint32_t pass=0;pass<5;pass++)for(uint32_t j=0;j<12;j++)op(minus,n,program[11-j],1);
 for(uint32_t i=0;i<n/2;i++){uint32_t t=minus[i];minus[i]=minus[n-1-i];minus[n-1-i]=t;}
 last_n=n;
}
static void crc_init(void){if(crc_initialized)return;for(uint32_t i=0;i<256;i++){uint32_t c=i;for(int j=0;j<8;j++)c=(c&1)?0xedb88320u^(c>>1):c>>1;crc_table[i]=c;}crc_initialized=1;}
static uint32_t crc32(const uint8_t *buf,uint32_t len){crc_init();uint32_t c=0xffffffffu;for(uint32_t i=0;i<len;i++)c=crc_table[(c^buf[i])&255u]^(c>>8);return c^0xffffffffu;}
static uint32_t read32(const uint8_t *b){return ((uint32_t)b[0]<<24)|((uint32_t)b[1]<<16)|((uint32_t)b[2]<<8)|b[3];}
static void write32(uint8_t *b,uint32_t x){b[0]=(uint8_t)(x>>24);b[1]=(uint8_t)(x>>16);b[2]=(uint8_t)(x>>8);b[3]=(uint8_t)x;}
/* Encode reads input[0:n], writes frame[0:16+2*n], returns size or 0 on error. */
EXPORT("encode") uint32_t encode(uint32_t n){
 if(n>MAX_N)return 0;
 maps(n);frame[0]='O';frame[1]='B';frame[2]='F';frame[3]='2';
 frame[4]=1;frame[5]=1;frame[6]=0;frame[7]=0;write32(frame+8,n);
 for(uint32_t i=0;i<n;i++){frame[12+i]=input[plus[i]];frame[12+n+i]=input[minus[i]];}
 uint32_t len=OVER+2*n;write32(frame+len-4,crc32(frame,len-4));return len;
}
/* Decode reads supplied frame[0:wire_len]; validates CRC and dual rails.
 * Returns source byte count on success, -1 for invalid frame. */
EXPORT("decode") int32_t decode(uint32_t wire_len){
 if(wire_len<OVER||wire_len>MAX_WIRE||frame[0]!='O'||frame[1]!='B'||frame[2]!='F'||frame[3]!='2'||
  frame[4]!=1||frame[5]!=1||frame[6]!=0||frame[7]!=0)return -1;
 uint32_t n=read32(frame+8);if(n>MAX_N||wire_len!=OVER+2*n)return -1;
 if(read32(frame+wire_len-4)!=crc32(frame,wire_len-4))return -1;
 maps(n);for(uint32_t i=0;i<n;i++)recovered[plus[i]]=frame[12+i];
 for(uint32_t i=0;i<n;i++)if(recovered[minus[i]]!=frame[12+n+i])return -1;
 return (int32_t)n;
}
/* Freestanding compiler-generated copies; no imported libc. */
void *memcpy(void *dest, const void *src, unsigned long n){
 uint8_t* d=(uint8_t*)dest;const uint8_t* s=(const uint8_t*)src;
 for(unsigned long i=0;i<n;i++)d[i]=s[i];return dest;
}
