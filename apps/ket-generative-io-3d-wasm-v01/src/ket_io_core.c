/* KET Generative I/O : frozen v2.0 overlay, no kernel mutations.
 * WASM: deterministic 360+3+3 toroidal geometry + discrete phase controller.
 * Compile with clang --target=wasm32 -O3 -nostdlib, --no-entry, --export-all.
 * No clock, no network, no external imports.
 */
#define MAJOR_STEPS 96
#define MINOR_STEPS 48
#define SURFACE_SKINS 20
#define SURFACE_SECTORS 18
#define NODE_COUNT (SURFACE_SKINS*SURFACE_SECTORS)
#define MESH_COUNT (MAJOR_STEPS*MINOR_STEPS)
#define PI 3.14159265358979323846264338327950288
#define TWO_PI (2.0*PI)
#define HALF_PI (0.5*PI)
static float mesh[MESH_COUNT * 7]; /* x y z normalx normaly normalz scalar */
static float nodes[NODE_COUNT * 4]; /* x y z deterministic variation */
static double speed = 1.0, phase = 0.0, baseline = 1.0, increment = 0.1;
static int simulation_tick = 0, last_command = 0;
static unsigned int seed_value = 42;

static double absd(double v) { return v < 0 ? -v : v; }
static double sin_approx(double x) {
  while (x > PI) x -= TWO_PI;
  while (x < -PI) x += TWO_PI;
  if (x > HALF_PI) x = PI-x;
  else if (x < -HALF_PI) x = -PI-x;
  double x2=x*x;
  /* Maclaurin, reduced to [-pi/2,pi/2]; near double precision. */
  return x*(1.0 + x2*(-1.0/6.0 + x2*(1.0/120.0 + x2*(-1.0/5040.0 + x2*(1.0/362880.0 + x2*(-1.0/39916800.0 + x2/6227020800.0))))));
}
static double cos_approx(double x) { return sin_approx(x+HALF_PI); }
static unsigned int hash32(unsigned int x) {
  x ^= x >> 16; x *= 0x7feb352dU; x ^= x >> 15; x *= 0x846ca68bU; x ^= x >> 16; return x;
}
static float variation(unsigned int idx) {return (float)(hash32(idx ^ seed_value) & 65535U) / 65535.0f;}

__attribute__((export_name("reset"))) void reset(double base, double delta, unsigned int seed) {
  if (base <= 0.0 || delta < 0.0 || 2.0*delta >= base) return;
  baseline=base; increment=delta; seed_value=seed;
  speed=baseline; phase=0.0; simulation_tick=0;last_command=0;
}
__attribute__((export_name("step"))) int step(void) {
  static const int command[12]={-1,-1,1,1,1,-1,1,1,-1,-1,-1,1};
  int i=simulation_tick % 360;
  last_command = i<12 ? command[i] : 0;
  speed += increment*(double)last_command;
  phase += speed;
  simulation_tick++;
  return last_command;
}
__attribute__((export_name("generate"))) int generate(double major, double minor, double twist) {
  if (major<=minor || minor<=0 || absd(twist)>1.0) return 0;
  for (int i=0;i<MINOR_STEPS;i++) {
    double a=(TWO_PI*i)/(double)MINOR_STEPS;
    for (int j=0;j<MAJOR_STEPS;j++) {
      double b=(TWO_PI*j)/(double)MAJOR_STEPS;
      double aa=a+twist*sin_approx(2.0*b);
      double ca=cos_approx(aa), sa=sin_approx(aa), cb=cos_approx(b), sb=sin_approx(b);
      double radius=major+minor*ca;
      int k=(i*MAJOR_STEPS+j)*7;
      mesh[k]=(float)(radius*cb); mesh[k+1]=(float)(radius*sb); mesh[k+2]=(float)(minor*sa);
      mesh[k+3]=(float)(ca*cb); mesh[k+4]=(float)(ca*sb); mesh[k+5]=(float)sa;
      mesh[k+6]=variation((unsigned int)(i*MAJOR_STEPS+j));
    }
  }
  for(int i=0;i<SURFACE_SKINS;i++) {
    double a=(TWO_PI*i)/(double)SURFACE_SKINS;
    for(int j=0;j<SURFACE_SECTORS;j++) {
      double b=(TWO_PI*j)/(double)SURFACE_SECTORS;
      double aa=a+twist*sin_approx(2.0*b);
      double radius=major+minor*cos_approx(aa);
      int k=(i*SURFACE_SECTORS+j)*4;
      nodes[k]=(float)(radius*cos_approx(b));
      nodes[k+1]=(float)(radius*sin_approx(b));
      nodes[k+2]=(float)(minor*sin_approx(aa));
      nodes[k+3]=variation((unsigned int)(i*SURFACE_SECTORS+j));
    }
  }
  return NODE_COUNT;
}
__attribute__((export_name("get_tick"))) int get_tick(void){return simulation_tick;}
__attribute__((export_name("get_phase"))) double get_phase(void){return phase;}
__attribute__((export_name("get_speed"))) double get_speed(void){return speed;}
__attribute__((export_name("get_last_command"))) int get_last_command(void){return last_command;}
__attribute__((export_name("mesh_ptr"))) int mesh_ptr(void){return (int)mesh;}
__attribute__((export_name("mesh_count"))) int mesh_count(void){return MESH_COUNT;}
__attribute__((export_name("nodes_ptr"))) int nodes_ptr(void){return (int)nodes;}
__attribute__((export_name("nodes_count"))) int nodes_count(void){return NODE_COUNT;}
__attribute__((export_name("get_seed"))) int get_seed(void){return (int)seed_value;}
