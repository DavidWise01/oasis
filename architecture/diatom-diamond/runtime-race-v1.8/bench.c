#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
static const char CODE[]="UUDDLRLRBASS";
static void op(uint8_t a[32],char op,int inv){
 if(op=='U'||op=='D'||op=='A'){int k=op=='U'?1:op=='D'?-1:2;if(inv)k=-k;k=(k%32+32)%32;uint8_t tmp[32];for(int i=0;i<32;i++)tmp[(i+k)%32]=a[i];memcpy(a,tmp,32);}
 else if(op=='L'||op=='R'){int off=op=='L'?0:1;for(int i=off;i+1<32;i+=2){uint8_t t=a[i];a[i]=a[i+1];a[i+1]=t;}}
 else if(op=='B'){for(int i=0;i<16;i++){uint8_t t=a[i];a[i]=a[31-i];a[31-i]=t;}}
}
static void perm(uint8_t a[32],int inv){for(int p=0;p<5;p++)for(int s=0;s<12;s++)op(a,CODE[inv?11-s:s],inv);}
static double stamp(){struct timespec ts;clock_gettime(CLOCK_MONOTONIC,&ts);return ts.tv_sec+ts.tv_nsec*1e-9;}
int main(int argc,char**argv){int n=argc>1?atoi(argv[1]):32768;if(n<=0||n%32)exit(2);double start=stamp();uint32_t check=2166136261u;
 for(int first=0;first<n;first+=32){uint8_t src[32],pos[32],neg[32],left[32],right[32];for(int j=0;j<32;j++)src[j]=(uint8_t)((first+j)%44);memcpy(pos,src,32);for(int j=0;j<32;j++)neg[j]=src[31-j];
 perm(pos,0);perm(neg,1);memcpy(left,pos,32);memcpy(right,neg,32);perm(left,1);perm(right,0);
 for(int j=0;j<32;j++)if(left[j]!=src[j]||right[31-j]!=src[j]){puts("ERROR");exit(3);}
 for(int i=0;i<32;i++)check=(check^pos[i])*16777619u;for(int i=0;i<32;i++)check=(check^neg[i])*16777619u;
 }
 printf("{\"runtime\":\"c\",\"tokens\":%d,\"checksum\":%u,\"elapsed_s\":%.9f}\n",n,check,stamp()-start);
}
