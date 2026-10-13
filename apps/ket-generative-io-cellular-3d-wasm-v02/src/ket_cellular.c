/* KET / Generative Cellular I/O v0.2. Pure WASM computational state.
 * Frozen 360+3+3 toroidal controller is read-only; this is an adapter.
 * Cell positions are SYMBOLIC Planck-point (pp) coordinates, not physical Planck physics.
 */
#include <stdint.h>
#define U 20
#define V 18
#define PORTS 360
#define MAX_LAYERS 6
#define MAX_CELLS (PORTS * MAX_LAYERS)
#define PI 3.14159265358979323846264338327950288
#define TWOPI (2.*PI)
#define HALFPI (PI/2.)
static float xyz[MAX_CELLS*3];
static int8_t cells[MAX_CELLS], scratch[MAX_CELLS];
static uint8_t ages[MAX_CELLS];
static int layers=3, count=1080, generation=0, clock_tick=0, last_sign=0;
static int active=0, refractory=0, births=0, threshold=2, pulse=9;
static uint32_t seed=42, checksum=0;
static double major=2.4, minor=.88, twist=.14;
static double base=1., delta=.1, omega=1., phase=0.;

static double sinfast(double x){
  while(x>PI)x-=TWOPI;while(x<-PI)x+=TWOPI;
  if(x>HALFPI)x=PI-x;else if(x<-HALFPI)x=-PI-x;
  double q=x*x;
  return x*(1.+q*(-1./6.+q*(1./120.+q*(-1./5040.+q*(1./362880.+q*(-1./39916800.+q/6227020800.))))));
}
static double cosfast(double x){return sinfast(x+HALFPI);}
static uint32_t hash32(uint32_t n){n^=n>>16;n*=0x7feb352dU;n^=n>>15;n*=0x846ca68bU;n^=n>>16;return n;}
static int index3(int u,int v,int d){
  if(u<0)u+=U; if(u>=U)u-=U;
  if(v<0)v+=V; if(v>=V)v-=V;
  if(d<0||d>=layers)return -1;
  return (u*V+v)*layers+d;
}
static uint32_t state_hash(void){
  uint32_t h=2166136261U;
  for(int i=0;i<count;i++){h^=(uint32_t)(cells[i]+1);h*=16777619U;h^=ages[i];h*=16777619U;}
  h^=(uint32_t)generation; h*=16777619U;
  return h;
}
__attribute__((export_name("configure"))) int configure(double R,double r,double t,int L,uint32_t s,int thresh,int pulse_permille,double b,double dd){
  if(!(R>r&&r>0.) || R>10. || r>5. || t>1. || t< -1. || L<1 || L>MAX_LAYERS || thresh<1 || thresh>5 || pulse_permille<0 || pulse_permille>60 || b<=2.*dd || dd<0. || b>5. || dd>1.)return 0;
  major=R;minor=r;twist=t;layers=L;seed=s;threshold=thresh;pulse=pulse_permille;base=b;delta=dd;
  omega=base;phase=0.;generation=0;clock_tick=0;last_sign=0;active=0;refractory=0;births=0;
  count=PORTS*layers;
  for(int u=0;u<U;u++)for(int v=0;v<V;v++)for(int d=0;d<layers;d++){
    int i=index3(u,v,d);
    double a=TWOPI*(double)v/V, bphi=TWOPI*(double)u/U;
    double aa=a+twist*sinfast(2.*bphi);
    double rho=minor*(.22+.78*(double)(d+1)/(double)layers);
    double ring=major+rho*cosfast(aa);
    xyz[i*3]=(float)(ring*cosfast(bphi));
    xyz[i*3+1]=(float)(rho*sinfast(aa));
    xyz[i*3+2]=(float)(ring*sinfast(bphi));
    uint32_t h=hash32(s^hash32((uint32_t)(i+17)*0x9e3779b9U));
    int pick=(int)(h%1000U);
    cells[i]=(pick<158)?1:(pick<210?-1:0);
    ages[i]=(cells[i]==1)?1:0;
    if(cells[i]==1)active++;else if(cells[i]==-1)refractory++;
  }
  checksum=state_hash();return count;
}
__attribute__((export_name("advance"))) int advance(void){
  static const int controls[12]={-1,-1,1,1,1,-1, 1,1,-1,-1,-1,1};
  int k=clock_tick%360;
  last_sign=(k<12)?controls[k]:0;
  omega+=delta*(double)last_sign;
  phase+=omega;
  clock_tick++;generation++;
  int local_threshold=threshold + (last_sign<0?1:(last_sign>0?-1:0));
  if(local_threshold<1)local_threshold=1;
  active=0;refractory=0;births=0;
  for(int u=0;u<U;u++)for(int v=0;v<V;v++)for(int d=0;d<layers;d++){
    int i=index3(u,v,d);
    int nb[6]={index3(u-1,v,d),index3(u+1,v,d),index3(u,v-1,d),index3(u,v+1,d),index3(u,v,d-1),index3(u,v,d+1)};
    int excit=0;
    for(int j=0;j<6;j++) if(nb[j]>=0 && cells[nb[j]]==1)excit++;
    if(cells[i]==1)scratch[i]=-1;
    else if(cells[i]==-1)scratch[i]=0;
    else{
      uint32_t h=hash32(seed^((uint32_t)generation*0x9e3779b9U)^(uint32_t)(i*733U+17U));
      int spontaneous=(int)(h%1000U)<pulse;
      scratch[i]=(excit>=local_threshold || spontaneous)?1:0;
      if(scratch[i]==1)births++;
    }
  }
  for(int i=0;i<count;i++){
    if(scratch[i]==1){active++;ages[i]=(ages[i]<255)?ages[i]+1:255;}
    else if(scratch[i]==-1){refractory++;ages[i]=0;}
    else ages[i]=0;
    cells[i]=scratch[i];
  }
  checksum=state_hash();return active;
}
__attribute__((export_name("xyz_ptr"))) int xyz_ptr(void){return (int)(uintptr_t)xyz;}
__attribute__((export_name("cells_ptr"))) int cells_ptr(void){return (int)(uintptr_t)cells;}
__attribute__((export_name("ages_ptr"))) int ages_ptr(void){return (int)(uintptr_t)ages;}
__attribute__((export_name("cell_count"))) int cell_count(void){return count;}
__attribute__((export_name("get_layers"))) int get_layers(void){return layers;}
__attribute__((export_name("get_generation"))) int get_generation(void){return generation;}
__attribute__((export_name("get_tick"))) int get_tick(void){return clock_tick;}
__attribute__((export_name("get_active"))) int get_active(void){return active;}
__attribute__((export_name("get_refractory"))) int get_refractory(void){return refractory;}
__attribute__((export_name("get_births"))) int get_births(void){return births;}
__attribute__((export_name("get_sign"))) int get_sign(void){return last_sign;}
__attribute__((export_name("get_speed"))) double get_speed(void){return omega;}
__attribute__((export_name("get_phase"))) double get_phase(void){return phase;}
__attribute__((export_name("get_checksum"))) int get_checksum(void){return (int)checksum;}
__attribute__((export_name("get_seed"))) int get_seed(void){return (int)seed;}
__attribute__((export_name("get_threshold"))) int get_threshold(void){return threshold;}
__attribute__((export_name("get_pulse"))) int get_pulse(void){return pulse;}
