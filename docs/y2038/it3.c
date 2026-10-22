#include <stdint.h>
#include <stdbool.h>
#include <limits.h>
#include <stdio.h>
#include <inttypes.h>

#define DAY INT64_C(86400)
static void put64(uint8_t *p, uint64_t x) {
    for (int j=7;j>=0;--j) {p[j]=(uint8_t)x;x>>=8;}
}
static uint64_t get64(const uint8_t *p) {
    uint64_t x=0;for(int j=0;j<8;++j)x=(x<<8)|p[j];return x;
}
static void put32(uint8_t *p,uint32_t x) {
    for(int j=3;j>=0;--j){p[j]=(uint8_t)x;x>>=8;}
}
static uint32_t get32(const uint8_t *p) {
    uint32_t x=0;for(int j=0;j<4;++j)x=(x<<8)|p[j];return x;
}
static int64_t signed64(uint64_t u) {
    if(u<=INT64_MAX)return (int64_t)u;
    return -1-(int64_t)(UINT64_MAX-u);
}
static void split(int64_t t,int64_t *q,uint32_t *phase) {
    int64_t a=t/DAY,r=t%DAY;
    if(r<0){--a;r+=DAY;}
    *q=a;*phase=(uint32_t)r;
}
static bool encode(int64_t t,uint8_t out[16]) {
    if(!out)return false;
    int64_t q;uint32_t p;split(t,&q,&p);
    out[0]=0x49;out[1]=0x54;out[2]=0x33;out[3]=1;
    put64(out+4,(uint64_t)q);
    put32(out+12,((uint32_t)(q%2!=0)<<31)|p);
    return true;
}
static bool decode(const uint8_t *in,size_t n,int64_t *out) {
    if(!in||!out||n!=16)return false;
    if(in[0]!=0x49||in[1]!=0x54||in[2]!=0x33||in[3]!=1)return false;
    int64_t q=signed64(get64(in+4));
    uint32_t f=get32(in+12),p=f&UINT32_C(0x1ffff);
    if((f&UINT32_C(0x7ffe0000))!=0||p>=86400)return false;
    if((f>>31)!=(uint32_t)(q%2!=0))return false;
    int64_t minq,maxq;uint32_t minp,maxp;
    split(INT64_MIN,&minq,&minp);split(INT64_MAX,&maxq,&maxp);
    if(q<minq||q>maxq)return false;
    if(q==minq&&p<minp)return false;
    if(q==maxq&&p>maxp)return false;
    *out=q<0?(q+1)*DAY+((int64_t)p-DAY):q*DAY+(int64_t)p;
    return true;
}
static void dump(const uint8_t b[16]) {
    for(int i=0;i<16;i++)printf("%02X%s",b[i],i==15?"\n":" ");
}
int main(void) {
    const int64_t cases[]={INT64_MIN,-INT64_C(2147483649),-1,0,
        INT64_C(2147483647),INT64_C(2147483648),
        INT64_C(4102444800),INT64_MAX};
    int failed=0;
    for(size_t i=0;i<sizeof cases/sizeof *cases;i++){
        uint8_t packet[16];int64_t got=0;
        bool ok=encode(cases[i],packet)&&decode(packet,16,&got)&&got==cases[i];
        printf("t=%" PRId64 " : %s  ",cases[i],ok?"PASS":"FAIL");dump(packet);
        if(!ok)failed++;
        uint8_t corrupt[16];
        for(int j=0;j<16;j++)corrupt[j]=packet[j];
        corrupt[12]^=0x40;
        if(decode(corrupt,16,&got))failed++;
    }
    printf("Result: %s\n",failed?"FAIL":"PASS");
    return failed?1:0;
}
