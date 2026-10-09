// OaSIs SHEET95 — bounded adaptive swept-path recovery + causal delivery ACK; freestanding WASM32.
// Swept 3D 2-segment polyline clearance before via grants.
// 8 physical silo/domains D0..D7, one logical aggregate D8, 8 slots FIFO.
// Admission: per-domain oldest waiting lane, domain-round-robin; no packet loss.
#define LANES 120
#define FLOORS 8
#define DOMAINS 9
#define AGGREGATE 8
#define TOROIDS 9
#define COPPER 11
#define OCTETS 4
#define SCALE 1000000
#define VIA_TICKS 24
#define AGG_TICKS 8
#define CAPACITY 8
#define ACK_TICKS 5
// Symbolic geometric units (not millimeters). 3D x/y 8 units between ring anchors,
// 12 units between silo floors, copper subplanes at z increments of 0.3.
// Neighboring routes bend toward each other at the 12-tick midpoint.
#define CLEARANCE2 2.25 // minimum 3D centerline separation 1.5 units
static int floor_no[LANES],ring[LANES],copper[LANES],bank[LANES],cell[LANES];
static int progress[LANES],speed[LANES],phase[LANES],via_tick[LANES],agg_tick[LANES],hops[LANES];
static int source_floor[LANES],target_floor[LANES],source_copper[LANES],target_copper[LANES];
static int source_bank[LANES],target_bank[LANES],kind[LANES],domain[LANES];
// phase: 0 ORBIT, 1 VIA_BUSY, 2 D8_QUEUED, 3 D8_WAIT, 4 CLEARANCE_HOLD, 5 ACK_PENDING
static int clearance_tick[LANES],ack_tick[LANES],delivery_seq[LANES],ack_seq[LANES];
static int clearance_grants=0,clearance_deferrals=0,clearance_hold_ticks=0;
static int peak_active_vias=0,peak_clearance_holds=0,deliveries=0,acks=0;
static int swept_deferrals=0,swept_cross_ring_deferrals=0,swept_grants=0;
static int active_swept_conflicts=0;
// Policy 0: exact fixed-route SHEET94 baseline. Policy 1: 4-option causal recovery.
// Variant 0 original center bend, 1 straight midpoint, 2 y-lateral, 3 outward x-bend.
static int routing_policy=1,route_mode[LANES];
static int proposals=0,adaptive_grants=0,hard_holds=0;
static int route_length_milli=0; // cumulative Euclidean waypoint length per granted route
static int max_adaptive_displacement_milli=3600;

static int arrival_tick[LANES], domain_entries[DOMAINS],domain_exits[DOMAINS],serviced_by_silo[FLOORS];
static int queue[CAPACITY],qhead=0,qtail=0,qcount=0,rr_next=0;
static int ticks=0,orbits=0,vias=0,floor_vias=0,zero_gates=0;
static int aggregate_in=0,aggregate_out=0,waiting=0,blocked_ticks=0,waiter_ticks=0;
static int max_waiting=0,max_queue=0,max_wait_ticks=0,domain_crossings=0,pressure_ticks=0;
static int reflect(int n,int limit,int sign){int v=n+sign;return v<0?1:(v>=limit?limit-2:v);}
__attribute__((export_name("reset"))) void reset(void){
 ticks=orbits=vias=floor_vias=zero_gates=0;aggregate_in=aggregate_out=waiting=blocked_ticks=waiter_ticks=0;
 max_waiting=max_queue=max_wait_ticks=domain_crossings=pressure_ticks=0;
 clearance_grants=clearance_deferrals=clearance_hold_ticks=0;
 peak_active_vias=peak_clearance_holds=deliveries=acks=0;
 swept_deferrals=swept_cross_ring_deferrals=swept_grants=active_swept_conflicts=0;
 proposals=adaptive_grants=hard_holds=route_length_milli=0;
 qhead=qtail=qcount=rr_next=0;
 for(int j=0;j<CAPACITY;j++)queue[j]=-1;
 for(int d=0;d<DOMAINS;d++)domain_entries[d]=domain_exits[d]=0;
 for(int f=0;f<FLOORS;f++)serviced_by_silo[f]=0;
 for(int i=0;i<LANES;i++){
  floor_no[i]=i%FLOORS;domain[i]=floor_no[i];ring[i]=i%TOROIDS;copper[i]=i%COPPER;
  bank[i]=(i/8)%OCTETS;cell[i]=i%8;
  progress[i]=(i*7919)%SCALE;speed[i]=3800+(i*83)%5800;
  phase[i]=via_tick[i]=agg_tick[i]=hops[i]=kind[i]=arrival_tick[i]=0;
  clearance_tick[i]=ack_tick[i]=delivery_seq[i]=ack_seq[i]=route_mode[i]=0;
  source_floor[i]=target_floor[i]=floor_no[i];
  source_copper[i]=target_copper[i]=copper[i];
  source_bank[i]=target_bank[i]=bank[i];domain_entries[domain[i]]++;
 }
}
// Deterministic synchronized stress: all 120 lanes complete a floor orbit next tick.
__attribute__((export_name("stress_all"))) void stress_all(void){
 reset();
 for(int i=0;i<LANES;i++){progress[i]=SCALE-speed[i];hops[i]=2;}
}
static void begin_via(int i){
 route_mode[i]=0;
 progress[i]=SCALE;orbits++;phase[i]=4;via_tick[i]=0;clearance_tick[i]=0;
 source_floor[i]=target_floor[i]=floor_no[i];
 source_copper[i]=target_copper[i]=copper[i];
 source_bank[i]=target_bank[i]=bank[i];
 kind[i]=(hops[i]%3==2)?2:1;
 if(kind[i]==1)target_copper[i]=reflect(copper[i],COPPER,(i&1)?-1:1);
 else {target_floor[i]=reflect(floor_no[i],FLOORS,(i&1)?-1:1);target_bank[i]=(bank[i]+1)%OCTETS;}
}
// x/y/z pathway: P0 -> MID -> P2, with a 3D bend at the midpoint.
// The same immutable planned path is checked before grant and during VIA_ACTIVE.
// This checks full spatial polylines, NOT merely synchronized positions.
typedef struct {double x,y,z;} Vec;
static Vec xyz(double x,double y,double z){Vec v={x,y,z};return v;}
static Vec sub(Vec a,Vec b){return xyz(a.x-b.x,a.y-b.y,a.z-b.z);}
static Vec add(Vec a,Vec b){return xyz(a.x+b.x,a.y+b.y,a.z+b.z);}
static Vec mul(Vec a,double t){return xyz(a.x*t,a.y*t,a.z*t);}
static double dot(Vec a,Vec b){return a.x*b.x+a.y*b.y+a.z*b.z;}
static double clamp01(double x){return x<0?0:x>1?1:x;}
static Vec endpoint(int i,int dest){
 int f=dest?target_floor[i]:source_floor[i];
 int c=dest?target_copper[i]:source_copper[i];
 int r=ring[i];
 return xyz(8.0*(r%3),8.0*(r/3),12.0*f+0.3*(c-5));
}
static Vec waypoint_mode(int i,int mode){
 Vec a=endpoint(i,0),b=endpoint(i,1);
 double xshift=0.0,yshift=0.0;
 int col=ring[i]%3;
 if(mode==0)xshift=col==0?3.6:(col==1?-3.6:0.0);
 else if(mode==2)yshift=(ring[i]/3==0?3.6:-3.6); // inside synthetic bounds
 else if(mode==3)xshift=col==0?-3.6:(col==1?3.6:0.0);
 return xyz(0.5*(a.x+b.x)+xshift,0.5*(a.y+b.y)+yshift,0.5*(a.z+b.z));
}
static Vec waypoint(int i){return waypoint_mode(i,route_mode[i]);}
static double length3(Vec a,Vec b){Vec d=sub(a,b);return __builtin_sqrt(dot(d,d));}
static int planned_length_milli(int i){Vec a=endpoint(i,0),m=waypoint(i),b=endpoint(i,1);return (int)((length3(a,m)+length3(m,b))*1000+0.5);}
// Squared closest separation of two closed 3D segments. Degenerate cases included.
static double segdist2(Vec p0,Vec p1,Vec q0,Vec q1){
 Vec u=sub(p1,p0),v=sub(q1,q0),w=sub(p0,q0);
 double a=dot(u,u),b=dot(u,v),c=dot(v,v),d=dot(u,w),e=dot(v,w),D=a*c-b*b;
 double sc,tc,sN,sD=D,tN,tD=D;
 const double eps=1e-12;
 if(a<eps&&c<eps)return dot(w,w);
 if(a<eps){tc=clamp01(e/c);Vec diff=sub(p0,add(q0,mul(v,tc)));return dot(diff,diff);}
 if(c<eps){sc=clamp01(-d/a);Vec diff=sub(add(p0,mul(u,sc)),q0);return dot(diff,diff);}
 if(D<eps){sN=0;sD=1;tN=e;tD=c;}
 else {sN=b*e-c*d;tN=a*e-b*d;
  if(sN<0){sN=0;tN=e;tD=c;}
  else if(sN>sD){sN=sD;tN=e+b;tD=c;}
 }
 if(tN<0){tN=0;if(-d<0)sN=0;else if(-d>a)sN=sD;else{sN=-d;sD=a;}}
 else if(tN>tD){tN=tD;if(-d+b<0)sN=0;else if(-d+b>a)sN=sD;else{sN=-d+b;sD=a;}}
 sc=sN==0?0:sN/sD;tc=tN==0?0:tN/tD;
 Vec diff=sub(add(w,mul(u,sc)),mul(v,tc));return dot(diff,diff);
}
static double route_dist2(int i,int j){
 Vec p[3]={endpoint(i,0),waypoint(i),endpoint(i,1)};
 Vec q[3]={endpoint(j,0),waypoint(j),endpoint(j,1)};
 double best=1e100;
 for(int a=0;a<2;a++)for(int b=0;b<2;b++){
  double d2=segdist2(p[a],p[a+1],q[b],q[b+1]);if(d2<best)best=d2;
 }
 return best;
}
static int candidate_clear(int i,int *cross_ring){
 for(int j=0;j<LANES;j++)if(j!=i&&phase[j]==1){
  if(route_dist2(i,j)<CLEARANCE2){if(ring[i]!=ring[j])*cross_ring=1;return 0;}
 }
 return 1;
}
// Never adapt a currently active via. Test full immutable candidate centerlines.
static int choose_available_path(int i){
 int cross_any=0;
 int max_modes=routing_policy?4:1;
 for(int mode=0;mode<max_modes;mode++){
  route_mode[i]=mode;proposals++;
  int cross=0;
  if(candidate_clear(i,&cross)){
   if(mode>0)adaptive_grants++;
   route_length_milli+=planned_length_milli(i);
   return 1;
  }
  cross_any|=cross;
 }
 route_mode[i]=0;hard_holds++;swept_deferrals++;
 if(cross_any)swept_cross_ring_deferrals++;
 return 0;
}
static void commit_head(void){
 int i=queue[qhead];queue[qhead]=-1;qhead=(qhead+1)%CAPACITY;qcount--;
 domain_exits[AGGREGATE]++;aggregate_out++;
 floor_no[i]=target_floor[i];domain[i]=floor_no[i];domain_entries[domain[i]]++;
 bank[i]=target_bank[i];floor_vias++;domain_crossings++;
 if(source_bank[i]<3)zero_gates++;
 serviced_by_silo[source_floor[i]]++;
 phase[i]=5;ack_tick[i]=0;via_tick[i]=agg_tick[i]=progress[i]=0;
 delivery_seq[i]++;deliveries++;hops[i]++;vias++;
}
static void admit_one(void){
 if(qcount>=CAPACITY||waiting==0)return;
 // Each admission chooses the oldest waiting lane of the next nonempty silo.
 int chosen=-1,chosen_domain=-1;
 for(int turn=0;turn<FLOORS;turn++){
  int d=(rr_next+turn)%FLOORS, best=-1;
  for(int i=0;i<LANES;i++)if(phase[i]==3&&source_floor[i]==d){
   if(best==-1||arrival_tick[i]<arrival_tick[best]||(arrival_tick[i]==arrival_tick[best]&&i<best))best=i;
  }
  if(best>=0){chosen=best;chosen_domain=d;break;}
 }
 if(chosen<0)return;
 rr_next=(chosen_domain+1)%FLOORS;
 waiting--;int delay=ticks-arrival_tick[chosen];if(delay>max_wait_ticks)max_wait_ticks=delay;
 domain_exits[domain[chosen]]++;domain[chosen]=AGGREGATE;domain_entries[AGGREGATE]++;
 aggregate_in++;phase[chosen]=2;agg_tick[chosen]=0;
 queue[qtail]=chosen;qtail=(qtail+1)%CAPACITY;qcount++;
 if(qcount>max_queue)max_queue=qcount;
}
__attribute__((export_name("step"))) void step(void){
 ticks++;
 for(int i=0;i<LANES;i++){
  if(phase[i]==0){progress[i]+=speed[i];if(progress[i]>=SCALE)begin_via(i);}
  else if(phase[i]==5){
   ack_tick[i]++;
   if(ack_tick[i]>=ACK_TICKS){ack_seq[i]++;acks++;phase[i]=0;ack_tick[i]=0;}
  }
  else if(phase[i]==1){
   via_tick[i]++;
   if(via_tick[i]>=VIA_TICKS){
    if(kind[i]==2){phase[i]=3;arrival_tick[i]=ticks;waiting++;}
    else {copper[i]=target_copper[i];phase[i]=via_tick[i]=progress[i]=0;hops[i]++;vias++;}
   }
  }
 }
 // Grant only available via tracks, in deterministic lane ID order.
 // Phase 4 retains a packet at its source anchor until reservation succeeds.
 int active=0,held=0;
 for(int i=0;i<LANES;i++)if(phase[i]==4){
  clearance_tick[i]++;clearance_hold_ticks++;held++;
  if(choose_available_path(i)){
   phase[i]=1;via_tick[i]=0;clearance_grants++;swept_grants++;held--;
  }else clearance_deferrals++;
 }
 for(int i=0;i<LANES;i++)if(phase[i]==1)active++;
 if(active>peak_active_vias)peak_active_vias=active;
 if(held>peak_clearance_holds)peak_clearance_holds=held;
 // Sweep all currently active 3D polylines; any violation is an engine fault.
 active_swept_conflicts=0;
 for(int i=0;i<LANES;i++)if(phase[i]==1)
  for(int j=i+1;j<LANES;j++)if(phase[j]==1&&route_dist2(i,j)<CLEARANCE2)active_swept_conflicts++;
 // The oldest admitted request is serviced without looking into future ticks.
 if(qcount>0){int i=queue[qhead];agg_tick[i]++;if(agg_tick[i]>=AGG_TICKS)commit_head();}
 // Admit at most one candidate per tick, with bounded aggregate occupancy.
 admit_one();
 waiter_ticks+=waiting;if(waiting>max_waiting)max_waiting=waiting;
 if(qcount==CAPACITY&&waiting>0){blocked_ticks++;pressure_ticks++;}
}
#define GET(name,data) __attribute__((export_name(#name))) int name(int i){return i>=0&&i<LANES?data[i]:-999;}
GET(get_floor,floor_no) GET(get_ring,ring) GET(get_copper,copper)
GET(get_bank,bank) GET(get_cell,cell) GET(get_progress,progress)
GET(get_speed,speed) GET(get_phase,phase) GET(get_via_tick,via_tick)
GET(get_agg_tick,agg_tick) GET(get_domain,domain) GET(get_arrival_tick,arrival_tick)
GET(get_source_floor,source_floor) GET(get_target_floor,target_floor)
GET(get_source_copper,source_copper) GET(get_target_copper,target_copper)
GET(get_source_bank,source_bank) GET(get_target_bank,target_bank)
GET(get_kind,kind) GET(get_hops,hops)
GET(get_clearance_tick,clearance_tick) GET(get_ack_tick,ack_tick)
GET(get_delivery_seq,delivery_seq) GET(get_ack_seq,ack_seq)
__attribute__((export_name("get_queue_lane"))) int get_queue_lane(int k){return k>=0&&k<qcount?queue[(qhead+k)%CAPACITY]:-1;}
__attribute__((export_name("get_domain_entries"))) int get_domain_entries(int d){return d>=0&&d<DOMAINS?domain_entries[d]:-999;}
__attribute__((export_name("get_domain_exits"))) int get_domain_exits(int d){return d>=0&&d<DOMAINS?domain_exits[d]:-999;}
__attribute__((export_name("get_service_silo"))) int get_service_silo(int d){return d>=0&&d<FLOORS?serviced_by_silo[d]:-999;}
#define SCALAR(name,variable) __attribute__((export_name(#name))) int name(void){return variable;}
SCALAR(get_ticks,ticks) SCALAR(get_orbits,orbits) SCALAR(get_vias,vias)
SCALAR(get_floor_vias,floor_vias) SCALAR(get_zero_gates,zero_gates)
SCALAR(get_aggregate_in,aggregate_in) SCALAR(get_aggregate_out,aggregate_out)
SCALAR(get_aggregate_pending,qcount) SCALAR(get_queue_count,qcount)
SCALAR(get_waiting,waiting) SCALAR(get_blocked_ticks,blocked_ticks)
SCALAR(get_waiter_ticks,waiter_ticks) SCALAR(get_max_waiting,max_waiting)
SCALAR(get_max_queue,max_queue) SCALAR(get_max_wait_ticks,max_wait_ticks)
SCALAR(get_domain_crossings,domain_crossings) SCALAR(get_rr_next,rr_next)
SCALAR(get_lanes,LANES) SCALAR(get_floors,FLOORS)
SCALAR(get_domains,DOMAINS) SCALAR(get_aggregate_id,AGGREGATE)
SCALAR(get_toroids,TOROIDS) SCALAR(get_copper_layers,COPPER)
SCALAR(get_via_ticks,VIA_TICKS) SCALAR(get_aggregate_ticks,AGG_TICKS)
SCALAR(get_octet_banks,OCTETS) SCALAR(get_queue_capacity,CAPACITY)

SCALAR(get_ack_ticks,ACK_TICKS)
SCALAR(get_clearance_grants,clearance_grants)
SCALAR(get_clearance_deferrals,clearance_deferrals)
SCALAR(get_clearance_hold_ticks,clearance_hold_ticks)
SCALAR(get_peak_active_vias,peak_active_vias)
SCALAR(get_peak_clearance_holds,peak_clearance_holds)
SCALAR(get_deliveries,deliveries)
SCALAR(get_acks,acks)
__attribute__((export_name("get_ack_pending"))) int get_ack_pending(void){return deliveries-acks;}
__attribute__((export_name("get_active_vias"))) int get_active_vias(void){int n=0;for(int i=0;i<LANES;i++)n+=phase[i]==1;return n;}
__attribute__((export_name("get_clearance_waiting"))) int get_clearance_waiting(void){int n=0;for(int i=0;i<LANES;i++)n+=phase[i]==4;return n;}
__attribute__((export_name("get_clearance_conflicts"))) int get_clearance_conflicts(void){int n=0;for(int i=0;i<LANES;i++)if(phase[i]==1)for(int j=i+1;j<LANES;j++)if(phase[j]==1&&route_dist2(i,j)<CLEARANCE2)n++;return n;}

// Geometry and clearance diagnostics exposed to WASM JS and runtime unit tests.
SCALAR(get_swept_deferrals,swept_deferrals)
SCALAR(get_swept_cross_ring_deferrals,swept_cross_ring_deferrals)
SCALAR(get_swept_grants,swept_grants)
SCALAR(get_swept_conflicts,active_swept_conflicts)
__attribute__((export_name("get_swept_radius_milli"))) int get_swept_radius_milli(void){return 1500;}
// Adversarial geometry directly tests the difference from SHEET93 same-ring guard.
// Floor-0, ring 0 and ring 1 bend toward one another and violate clearance.
__attribute__((export_name("test_neighbor_path_dist_milli"))) int test_neighbor_path_dist_milli(void){
 // Pure synthetic polylines from adjacent rings in the same floor.
 Vec p0=xyz(0,0,0),pm=xyz(3.6,0,0.15),p1=xyz(0,0,0.3);
 Vec q0=xyz(8,0,0),qm=xyz(4.4,0,0.15),q1=xyz(8,0,0.3);
 double d=segdist2(p0,pm,q0,qm), t=segdist2(pm,p1,qm,q1);
 if(t<d)d=t;
 return (int)(__builtin_sqrt(d)*1000+0.5);
}

// SHEET95 additional WASM exports. Policy changes apply to newly requested routes
// only; active routes remain frozen until completion.
__attribute__((export_name("set_policy"))) void set_policy(int x){routing_policy=(x!=0);}
__attribute__((export_name("get_policy"))) int get_policy(void){return routing_policy;}
GET(get_route_mode,route_mode)
SCALAR(get_proposals,proposals)
SCALAR(get_adaptive_grants,adaptive_grants)
SCALAR(get_hard_holds,hard_holds)
SCALAR(get_route_length_milli,route_length_milli)
SCALAR(get_max_adaptive_displacement_milli,max_adaptive_displacement_milli)
__attribute__((export_name("get_route_mid_x_milli"))) int get_route_mid_x_milli(int i){return i>=0&&i<LANES?(int)(waypoint(i).x*1000+0.5):-999;}
__attribute__((export_name("get_route_mid_y_milli"))) int get_route_mid_y_milli(int i){return i>=0&&i<LANES?(int)(waypoint(i).y*1000+0.5):-999;}
__attribute__((export_name("get_route_mid_z_milli"))) int get_route_mid_z_milli(int i){return i>=0&&i<LANES?(int)(waypoint(i).z*1000+0.5):-999;}