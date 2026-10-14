using System;
using System.Diagnostics;
class Bench{
 const string CODE="UUDDLRLRBASS";
 static void Op(byte[] a,char x,bool inv){if(x=='U'||x=='D'||x=='A'){int k=x=='U'?1:x=='D'?-1:2;if(inv)k=-k;k=(k%32+32)%32;byte[] tmp=new byte[32];for(int i=0;i<32;i++)tmp[(i+k)%32]=a[i];Array.Copy(tmp,a,32);}else if(x=='L'||x=='R'){for(int i=x=='L'?0:1;i+1<32;i+=2)(a[i],a[i+1])=(a[i+1],a[i]);}else if(x=='B')Array.Reverse(a);}
 static void Perm(byte[] a,bool inv){for(int p=0;p<5;p++)for(int s=0;s<12;s++)Op(a,CODE[inv?11-s:s],inv);}
 static void Main(string[] args){int n=args.Length>0?int.Parse(args[0]):32768;var t=Stopwatch.StartNew();uint ck=2166136261;for(int first=0;first<n;first+=32){var src=new byte[32];for(int j=0;j<32;j++)src[j]=(byte)((first+j)%44);var pos=(byte[])src.Clone();var neg=(byte[])src.Clone();Array.Reverse(neg);Perm(pos,false);Perm(neg,true);var left=(byte[])pos.Clone();var right=(byte[])neg.Clone();Perm(left,true);Perm(right,false);Array.Reverse(right);for(int j=0;j<32;j++)if(left[j]!=src[j]||right[j]!=src[j])throw new Exception("mismatch");unchecked{foreach(byte x in pos)ck=(ck^x)*16777619;foreach(byte x in neg)ck=(ck^x)*16777619;}}Console.WriteLine($"{{\"runtime\":\"csharp\",\"tokens\":{n},\"checksum\":{ck},\"elapsed_s\":{t.Elapsed.TotalSeconds:F9}}}");}}
