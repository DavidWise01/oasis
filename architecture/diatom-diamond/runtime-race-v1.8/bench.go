package main
import("fmt";"os";"strconv";"time")
const CODE="UUDDLRLRBASS"
func op(a []byte,x byte,inv bool){if x=='U'||x=='D'||x=='A'{k:=1;if x=='D'{k=-1};if x=='A'{k=2};if inv{k=-k};k=((k%32)+32)%32;var tmp [32]byte;for i:=0;i<32;i++{tmp[(i+k)%32]=a[i]};copy(a,tmp[:])}else if x=='L'||x=='R'{off:=0;if x=='R'{off=1};for i:=off;i+1<32;i+=2{a[i],a[i+1]=a[i+1],a[i]}}else if x=='B'{for i:=0;i<16;i++{a[i],a[31-i]=a[31-i],a[i]}}}
func perm(a []byte,inv bool){for p:=0;p<5;p++{for s:=0;s<12;s++{i:=s;if inv{i=11-s};op(a,CODE[i],inv)}}}
func main(){n:=32768;if len(os.Args)>1{n,_=strconv.Atoi(os.Args[1])};if n<1||n%32!=0{panic("bad n")};start:=time.Now();var ck uint32=2166136261;for first:=0;first<n;first+=32{var src,pos,neg,left,right [32]byte;for j:=0;j<32;j++{src[j]=byte((first+j)%44)};copy(pos[:],src[:]);for j:=0;j<32;j++{neg[j]=src[31-j]};perm(pos[:],false);perm(neg[:],true);copy(left[:],pos[:]);copy(right[:],neg[:]);perm(left[:],true);perm(right[:],false);for j:=0;j<32;j++{if left[j]!=src[j]||right[31-j]!=src[j]{panic("mismatch")}};for _,x:=range pos{ck=(ck^uint32(x))*16777619};for _,x:=range neg{ck=(ck^uint32(x))*16777619}}
fmt.Printf("{\"runtime\":\"go\",\"tokens\":%d,\"checksum\":%d,\"elapsed_s\":%.9f}\n",n,ck,time.Since(start).Seconds())}
