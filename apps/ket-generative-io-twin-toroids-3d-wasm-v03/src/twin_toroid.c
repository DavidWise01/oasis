/* KET Rule 02 v0.3 :: Independent twin tori and optional local information link.
 * Actual WASM: toroidal 3D positions + cellular transition + interface delivery.
 * Frozen KET v2.0 source is NOT modified. Synthetic pp resolution, not physics.
 */
#include <stdint.h>
#define U 20
#define V 18
#define SURFACE (U*V)
#define DEPTH_MAX 5
#define MAXCELLS (2*SURFACE*DEPTH_MAX)
#define PI 3.1415926535897932384626433832795
#define TAU (2.0*PI)
#define PI2 (PI/2.0)
static float xyz[MAXCELLS*3];
static int8_t cells[MAXCELLS], next_cells[MAXCELLS];
static int layers=3, per_torus=1080, generation=0, clock_tick=0;
static int mode=0, port_a=0, port_b=0, tx_ab=0, tx_ba=0, last_ab=0, last_ba=0;
static int excited_a=0, excited_b=0;
static uint32_t seed=42, digest=0;
static double radius=1.9, tube=.65, gap=.8;
static double speed_a=1, speed_b=1, phase_a=0,phase_b=0;
static const int commands[12]={-1,-1,1,1,1,-1,1,1,-1,-1,-1,1};
static double sinfast(double x){
  while(x>PI)x-=TAU;while(x< -PI)x+=TAU;
  if(x>PI2)x=PI-x;else if(x< -PI2)x=-PI-x;
  double q=x*x;
  return x*(1.+q*(-1./6.+q*(1./120.+q*(-1./5040.+q*(1./362880.+q*(-1./39916800.+q/6227020800.))))));
}
static double cosfast(double x){return sinfast(x+PI2);}
static uint32_t hash32(uint32_t x){x^=x>>16;x*=0x7feb352dU;x^=x>>15;x*=0x846ca68bU;x^=x>>16;return x;}
static int idx(int tor,int u,int v,int z){
  if(u<0)u+=U;if(u>=U)u-=U;
  if(v<0)v+=V;if(v>=V)v-=V;
  if(z<0||z>=layers)return -1;
  return tor*per_torus+(u*V+v)*layers+z;
}
static int endpoint(int tor,int surface){return tor*per_torus+surface*layers+(layers-1);}
static void make_xyz(void){
  double center_shift=radius+tube+gap/2.;
  for(int tor=0;tor<2;tor++)for(int u=0;u<U;u++)for(int v=0;v<V;v++)for(int z=0;z<layers;z++){
    int i=idx(tor,u,v,z);double a=TAU*(double)u/U,b=TAU*(double)v/V;
    double local_r=tube*(.32+.68*((double)(z+1)/(double)layers));
    double around=radius+local_r*cosfast(b);
    double cx=(tor==0?-center_shift:center_shift);
    xyz[3*i]=(float)(cx+around*cosfast(a));
    xyz[3*i+1]=(float)(around*sinfast(a));
    xyz[3*i+2]=(float)(local_r*sinfast(b));
  }
}
static uint32_t state_hash(void){
  uint32_t h=2166136261U;
  for(int i=0;i<2*per_torus;i++){h^=(uint32_t)(cells[i]+1);h*=16777619U;}
  h^=(uint32_t)generation;h*=16777619U;
  h^=(uint32_t)tx_ab;h*=16777619U;h^=(uint32_t)tx_ba;h*=16777619U;
  return h;
}
__attribute__((export_name("configure"))) int configure(double R,double r,int L,double g,int pa,int pb,int link,uint32_t s,int density){
  if(!(R>r&&r>0&&R<8&&r<3) || !(g>=0&&g<=12) || L<1||L>DEPTH_MAX||pa<0||pa>=SURFACE||pb<0||pb>=SURFACE||link<0||link>3||density<0||density>250)return 0;
  radius=R;tube=r;gap=g;layers=L;per_torus=SURFACE*L;port_a=pa;port_b=pb;mode=link;seed=s;
  generation=0;clock_tick=0;tx_ab=tx_ba=last_ab=last_ba=0;
  speed_a=speed_b=1;phase_a=phase_b=0;excited_a=excited_b=0;
  make_xyz();
  for(int t=0;t<2;t++)for(int i=0;i<per_torus;i++){
    int j=t*per_torus+i;
    uint32_t h=hash32(seed^((uint32_t)(j+13)*0x9e3779b9U));
    cells[j]=(h%1000U < (uint32_t)density)?1:0;
    if(cells[j]==1){if(t==0)excited_a++;else excited_b++;}
  }
  digest=state_hash();return 2*per_torus;
}
__attribute__((export_name("set_gate"))) int set_gate(int link){if(link<0||link>3)return 0;mode=link;return 1;}
__attribute__((export_name("set_ports"))) int set_ports(int pa,int pb){if(pa<0||pa>=360||pb<0||pb>=360)return 0;port_a=pa;port_b=pb;return 1;}
__attribute__((export_name("set_gap"))) int set_gap(double g){if(!(g>=0&&g<=12))return 0;gap=g;make_xyz();return 1;}
__attribute__((export_name("stimulate"))) int stimulate(int tor,int surface){
  if(tor<0||tor>1||surface<0||surface>=360)return 0;
  int k=endpoint(tor,surface);
  if(cells[k]!=1){cells[k]=1;if(tor==0)excited_a++;else excited_b++;}
  digest=state_hash();return 1;
}
__attribute__((export_name("advance"))) int advance(void){
  int k=clock_tick%360, cmd=(k<12)?commands[k]:0;
  speed_a+=.1*(double)cmd;speed_b+=.1*(double)cmd;
  phase_a+=speed_a;phase_b+=speed_b;
  generation++;clock_tick++;last_ab=last_ba=0;
  for(int t=0;t<2;t++)for(int u=0;u<U;u++)for(int v=0;v<V;v++)for(int z=0;z<layers;z++){
    int i=idx(t,u,v,z);
    int near[6]={idx(t,u-1,v,z),idx(t,u+1,v,z),idx(t,u,v-1,z),idx(t,u,v+1,z),idx(t,u,v,z-1),idx(t,u,v,z+1)};
    int count=0;for(int j=0;j<6;j++)if(near[j]>=0&&cells[near[j]]==1)count++;
    int8_t now=cells[i];
    /* Excitable CA: 0->1 via neighbors, 1->-1, -1->0; sparse seeded external-independent activity. */
    uint32_t h=hash32(seed^(uint32_t)(i*733U+17U)^((uint32_t)generation*0x9e3779b9U));
    next_cells[i]=(now==1)?-1:(now==-1)?0:((count>=2||(h%1000U)<7)?1:0);
  }
  /* Sender is read from OLD state; receiver's NEXT state receives only if gate is enabled. */
  int srca=endpoint(0,port_a),srcb=endpoint(1,port_b);
  if((mode&1)&&cells[srca]==1){next_cells[srcb]=1;tx_ab++;last_ab=1;}
  if((mode&2)&&cells[srcb]==1){next_cells[srca]=1;tx_ba++;last_ba=1;}
  excited_a=excited_b=0;
  for(int i=0;i<2*per_torus;i++){
    cells[i]=next_cells[i];if(cells[i]==1){if(i<per_torus)excited_a++;else excited_b++;}
  }
  digest=state_hash();return excited_a+excited_b;
}
__attribute__((export_name("positions_ptr"))) int positions_ptr(void){return (int)(uintptr_t)xyz;}
__attribute__((export_name("cells_ptr"))) int cells_ptr(void){return (int)(uintptr_t)cells;}
__attribute__((export_name("cell_count"))) int cell_count(void){return 2*per_torus;}
__attribute__((export_name("one_count"))) int one_count(void){return per_torus;}
__attribute__((export_name("get_tick"))) int get_tick(void){return clock_tick;}
__attribute__((export_name("get_phase"))) double get_phase(int t){return t==0?phase_a:phase_b;}
__attribute__((export_name("get_speed"))) double get_speed(int t){return t==0?speed_a:speed_b;}
__attribute__((export_name("get_excited"))) int get_excited(int t){return t==0?excited_a:excited_b;}
__attribute__((export_name("get_gate"))) int get_gate(void){return mode;}
__attribute__((export_name("get_port"))) int get_port(int t){return t==0?port_a:port_b;}
__attribute__((export_name("get_gap"))) double get_gap(void){return gap;}
__attribute__((export_name("get_tx"))) int get_tx(int direction){return direction==0?tx_ab:tx_ba;}
__attribute__((export_name("get_last_tx"))) int get_last_tx(int direction){return direction==0?last_ab:last_ba;}
__attribute__((export_name("get_checksum"))) int get_checksum(void){return (int)digest;}
