// OaSIs SHEET101 — capacity-aware deadline-commitment gate layered onto SHEET100/SHEET99.
// OaSIs SHEET99 — bounded-wait SLA governor over bounded dual-channel D8 service + causal delivery ACK; freestanding WASM32.
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
// Path policy 0: fixed route. 1: four-option recovery; both scheduler conditions retain policy 1.
// Variant 0 original center bend, 1 straight midpoint, 2 y-lateral, 3 outward x-bend.
static int routing_policy=1,route_mode[LANES];
// D8 service policy 1 = original serial FIFO; 2 = two independent 8-tick logical service channels.
static int service_channels=2, peak_busy_channels=0, channel_busy_ticks=0;
// Governor policies: 0 RR; 1 least-issued+age; 2 demand-normalized+age; 3 SLA deadline-first.
static int fairness_policy=3, issued_by_silo[FLOORS], fairness_age_overrides=0, fairness_selections=0;
// Demand means a completed physical via enters the *eligible* D8 waiting stage.
// Eligibility differs from orbit creation and from ACK completion.
#define HIST_LIMIT 4096
static int requested_by_silo[FLOORS], waiting_ticks_by_silo[FLOORS], acknowledgements_by_silo[FLOORS];
static int wait_sum_by_silo[FLOORS],wait_max_by_silo[FLOORS];
static int wait_hist[FLOORS][HIST_LIMIT];
static int normalized_policy_admissions=0;
#define FAIR_AGE_LIMIT 96
#define SLA_TARGET 96 // scheduling objective, not an end-to-end guarantee
static int deadline_boosts=0, sla_admissions=0, overdue_admissions=0;
static int proposals=0,adaptive_grants=0,hard_holds=0;
static int route_length_milli=0; // cumulative Euclidean waypoint length per granted route
static int max_adaptive_displacement_milli=3600;

// SHEET101: this gate is a deadline-commitment contract filter, NOT a packet dropper.
// Only policy3 (strict oldest eligible) supports the rank-based impossibility bound.
// Status: 0=not yet D8 eligible, 1=capacity-not-ruled-out, 2=provably impossible
// under FIFO/2-worker optimistic remaining workload, 3=unchecked when gate OFF.
static int gate_enabled=1;
static int gate_status[LANES],gate_request_tick[LANES],gate_lower_bound_ticks[LANES];
static int gate_requests=0,gate_possible=0,gate_impossible=0,gate_unchecked=0;
static int gate_acks_possible=0,gate_acks_impossible=0,gate_acks_unchecked=0;
static int gate_late_possible=0,gate_late_impossible=0,gate_late_unchecked=0;
static int gate_admitted_possible=0,gate_admitted_impossible=0,gate_admitted_unchecked=0;
static int gate_request_by_silo[FLOORS],gate_possible_by_silo[FLOORS],gate_impossible_by_silo[FLOORS];
static int gate_late_by_silo[FLOORS],gate_candidate_late_admissions=0;
static int arrival_tick[LANES], domain_entries[DOMAINS],domain_exits[DOMAINS],serviced_by_silo[FLOORS];
static int queue[CAPACITY],qhead=0,qtail=0,qcount=0,rr_next=0;
static int ticks=0,orbits=0,vias=0,floor_vias=0,zero_gates=0;
static int aggregate_in=0,aggregate_out=0,waiting=0,blocked_ticks=0,waiter_ticks=0;
static int max_waiting=0,max_queue=0,max_wait_ticks=0,domain_crossings=0,pressure_ticks=0;

/* SHEET103: per-lane 2^3 dot-photon carrier, integrated into actual SHEET101.
 * An immutable 8-component permutation vector is represented by an XOR mask.
 * State[k] = (k XOR mask) + 1, matching SHEET102's 8x8 permutation.
 * A dot-time tick happens exactly once per completed successful via hop.
 * 101 simulation/frame ticks are independent from photon logical ticks.
 * Networking edge cost is independent of elapsed scheduler/frame time.
 * This is symbolic photon routing, not physical photon propagation.
 */
#define PHOTON_STATES 8
static int photon_mask[LANES],photon_tick[LANES],photon_cost[LANES];
static int photon_last_from[LANES],photon_last_to[LANES],photon_last_edge_cost[LANES];
static int total_photon_ticks=0,total_photon_cost=0;
static int photon_edge_cost(int a,int b){
 if(a<0||a>=8||b<0||b>=8||a==b)return -1;
 if((((a+1)&7)!=b) && (((b+1)&7)!=a) && ((a^b)!=4))return -1;
 int lo=a<b?a:b,hi=a>b?a:b;
 return 1+((lo*3+hi*5)%4);
}
/* All layer endpoints are neighboring addresses on the 8-node ring;
 * floor hops use D0..D7, conductor hops use copper%8 addressing.
 */
static void photon_hop(int lane,int from,int to){
 int e=photon_edge_cost(from,to);
 if(e<=0)return;  /* test harness detects missing transition */
 photon_mask[lane]^=from^to;
 photon_last_from[lane]=from;
 photon_last_to[lane]=to;
 photon_last_edge_cost[lane]=e;
 photon_tick[lane]++;total_photon_ticks++;
 photon_cost[lane]+=e;total_photon_cost+=e;
}
__attribute__((export_name("get_photon_dimension"))) int get_photon_dimension(void){return PHOTON_STATES;}
__attribute__((export_name("get_photon_state"))) int get_photon_state(int lane,int component){
 if(lane<0||lane>=LANES||component<0||component>=PHOTON_STATES)return -999;
 return ((component^photon_mask[lane])+1);
}
__attribute__((export_name("get_photon_tick"))) int get_photon_tick(int lane){return lane>=0&&lane<LANES?photon_tick[lane]:-999;}
__attribute__((export_name("get_photon_mask"))) int get_photon_mask(int lane){return lane>=0&&lane<LANES?photon_mask[lane]:-999;}
__attribute__((export_name("get_photon_cost"))) int get_photon_cost(int lane){return lane>=0&&lane<LANES?photon_cost[lane]:-999;}
__attribute__((export_name("get_photon_last_from"))) int get_photon_last_from(int lane){return lane>=0&&lane<LANES?photon_last_from[lane]:-999;}
__attribute__((export_name("get_photon_last_to"))) int get_photon_last_to(int lane){return lane>=0&&lane<LANES?photon_last_to[lane]:-999;}
__attribute__((export_name("get_photon_last_edge_cost"))) int get_photon_last_edge_cost(int lane){return lane>=0&&lane<LANES?photon_last_edge_cost[lane]:-999;}
__attribute__((export_name("get_photon_total_ticks"))) int get_photon_total_ticks(void){return total_photon_ticks;}
__attribute__((export_name("get_photon_total_cost"))) int get_photon_total_cost(void){return total_photon_cost;}
__attribute__((export_name("get_photon_edge_cost"))) int get_photon_edge_cost(int a,int b){return photon_edge_cost(a,b);}
__attribute__((export_name("get_photon_version"))) int get_photon_version(void){return 103;}

static int reflect(int n,int limit,int sign){int v=n+sign;return v<0?1:(v>=limit?limit-2:v);}
__attribute__((export_name("reset"))) void reset(void){
 ticks=orbits=vias=floor_vias=zero_gates=0;aggregate_in=aggregate_out=waiting=blocked_ticks=waiter_ticks=0;
 max_waiting=max_queue=max_wait_ticks=domain_crossings=pressure_ticks=0;
 clearance_grants=clearance_deferrals=clearance_hold_ticks=0;
 peak_active_vias=peak_clearance_holds=deliveries=acks=0;
 swept_deferrals=swept_cross_ring_deferrals=swept_grants=active_swept_conflicts=0;
 proposals=adaptive_grants=hard_holds=route_length_milli=0;
 qhead=qtail=qcount=rr_next=0;peak_busy_channels=channel_busy_ticks=0;
 total_photon_ticks=total_photon_cost=0;
 for(int j=0;j<CAPACITY;j++)queue[j]=-1;
 gate_requests=gate_possible=gate_impossible=gate_unchecked=0;
 gate_acks_possible=gate_acks_impossible=gate_acks_unchecked=0;
 gate_late_possible=gate_late_impossible=gate_late_unchecked=0;
 gate_admitted_possible=gate_admitted_impossible=gate_admitted_unchecked=0;
 gate_candidate_late_admissions=0;
 for(int d=0;d<DOMAINS;d++)domain_entries[d]=domain_exits[d]=0;
 for(int f=0;f<FLOORS;f++){
  gate_request_by_silo[f]=gate_possible_by_silo[f]=gate_impossible_by_silo[f]=gate_late_by_silo[f]=0;
  serviced_by_silo[f]=issued_by_silo[f]=requested_by_silo[f]=0;
  waiting_ticks_by_silo[f]=acknowledgements_by_silo[f]=0;
  wait_sum_by_silo[f]=wait_max_by_silo[f]=0;
  for(int k=0;k<HIST_LIMIT;k++)wait_hist[f][k]=0;
 }
 normalized_policy_admissions=0;deadline_boosts=sla_admissions=overdue_admissions=0;
 fairness_age_overrides=fairness_selections=0;
 for(int i=0;i<LANES;i++){
  photon_mask[i]=photon_tick[i]=photon_cost[i]=0;photon_last_from[i]=photon_last_to[i]=-1;photon_last_edge_cost[i]=0;
  floor_no[i]=i%FLOORS;domain[i]=floor_no[i];ring[i]=i%TOROIDS;copper[i]=i%COPPER;
  bank[i]=(i/8)%OCTETS;cell[i]=i%8;
  progress[i]=(i*7919)%SCALE;speed[i]=3800+(i*83)%5800;
  phase[i]=via_tick[i]=agg_tick[i]=hops[i]=kind[i]=arrival_tick[i]=0;
  gate_status[i]=gate_request_tick[i]=gate_lower_bound_ticks[i]=0;
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
// Skewed-burst benchmark: 15 immediate requests per silo D0-D3, only
// three immediate requests per silo D4-D7. Other identities continue orbiting.
__attribute__((export_name("stress_skew"))) void stress_skew(void){
 reset();
 for(int i=0;i<LANES;i++)if((i%FLOORS)<4 || (i/FLOORS)<3){progress[i]=SCALE-speed[i];hops[i]=2;}
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
// Optimistic *necessary* lower bound: complete every already eligible older request,
// then this new request. Existing in-flight service receives credit for work done.
// Ignore admission pacing, path clearance and new arrivals, making the bound safe
// for the unchanged strict-oldest (fairness_policy==3) service discipline.
static int gate_min_ack_ticks_new(void){
 int total=AGG_TICKS;
 for(int k=0;k<qcount;k++){
  int i=queue[(qhead+k)%CAPACITY];
  total+=AGG_TICKS-agg_tick[i];
 }
 total+=waiting*AGG_TICKS;
 return (total+service_channels-1)/service_channels+ACK_TICKS;
}
static void gate_on_eligible(int i){
 int d=source_floor[i],lb=gate_min_ack_ticks_new();
 gate_request_tick[i]=ticks;gate_lower_bound_ticks[i]=lb;
 int status=(!gate_enabled||fairness_policy!=3)?3:(lb>SLA_TARGET?2:1);
 gate_status[i]=status;gate_requests++;gate_request_by_silo[d]++;
 if(status==1){gate_possible++;gate_possible_by_silo[d]++;}
 if(status==2){gate_impossible++;gate_impossible_by_silo[d]++;}
 if(status==3)gate_unchecked++;
}
static void gate_on_ack(int i){
 int delay=ticks-gate_request_tick[i],d=source_floor[i];
 int late=delay>SLA_TARGET;
 if(gate_status[i]==1){gate_acks_possible++;gate_late_possible+=late;}
 else if(gate_status[i]==2){gate_acks_impossible++;gate_late_impossible+=late;}
 else if(gate_status[i]==3){gate_acks_unchecked++;gate_late_unchecked+=late;}
 if(late)gate_late_by_silo[d]++;
}
static void commit_head(void){
 int i=queue[qhead];queue[qhead]=-1;qhead=(qhead+1)%CAPACITY;qcount--;
 domain_exits[AGGREGATE]++;aggregate_out++;
 photon_hop(i,source_floor[i],target_floor[i]);
 floor_no[i]=target_floor[i];domain[i]=floor_no[i];domain_entries[domain[i]]++;
 bank[i]=target_bank[i];floor_vias++;domain_crossings++;
 if(source_bank[i]<3)zero_gates++;
 serviced_by_silo[source_floor[i]]++;
 phase[i]=5;ack_tick[i]=0;via_tick[i]=agg_tick[i]=progress[i]=0;
 delivery_seq[i]++;deliveries++;hops[i]++;vias++;
}
static void admit_one(void){
 if(qcount>=CAPACITY||waiting==0)return;
 // Baseline: source RR with oldest per-source FIFO. Governor: select the
 // least-issued source with a pending request, while preserving FIFO within
 // each source; requests older than FAIR_AGE_LIMIT take precedence globally.
 int chosen=-1,chosen_domain=-1;
 if(!fairness_policy){
  for(int turn=0;turn<FLOORS;turn++){
   int d=(rr_next+turn)%FLOORS,best=-1;
   for(int i=0;i<LANES;i++)if(phase[i]==3&&source_floor[i]==d){
    if(best==-1||arrival_tick[i]<arrival_tick[best]||(arrival_tick[i]==arrival_tick[best]&&i<best))best=i;
   }
   if(best>=0){chosen=best;chosen_domain=d;break;}
  }
 } else {
  int oldest=-1;
  for(int i=0;i<LANES;i++)if(phase[i]==3)
   if(oldest<0||arrival_tick[i]<arrival_tick[oldest]||(arrival_tick[i]==arrival_tick[oldest]&&i<oldest))oldest=i;
  if(oldest>=0&&ticks-arrival_tick[oldest]>=FAIR_AGE_LIMIT){
   chosen=oldest;chosen_domain=source_floor[oldest];fairness_age_overrides++;
  }else if(fairness_policy==1){
   int best_score=0x7fffffff,best_age=-1,best_turn=FLOORS+1;
   for(int turn=0;turn<FLOORS;turn++){
    int d=(rr_next+turn)%FLOORS,best=-1;
    for(int i=0;i<LANES;i++)if(phase[i]==3&&source_floor[i]==d)
     if(best<0||arrival_tick[i]<arrival_tick[best]||(arrival_tick[i]==arrival_tick[best]&&i<best))best=i;
    if(best<0)continue;
    int score=issued_by_silo[d],age=ticks-arrival_tick[best];
    if(chosen<0||score<best_score||(score==best_score&&(age>best_age||(age==best_age&&turn<best_turn)))){
     chosen=best;chosen_domain=d;best_score=score;best_age=age;best_turn=turn;
    }
   }
  }else if(fairness_policy==3){
   // Earliest-eligible first. A pending request has priority over every
   // younger waiting request. This guarantees no overtaking in D8 admission,
   // but cannot guarantee a finite time bound under unbounded arrivals.
   int best=-1;
   for(int i=0;i<LANES;i++)if(phase[i]==3)
    if(best<0||arrival_tick[i]<arrival_tick[best]||
      (arrival_tick[i]==arrival_tick[best]&&i<best))best=i;
   chosen=best;chosen_domain=best<0?-1:source_floor[best];
   if(chosen>=0&&ticks-arrival_tick[chosen]>=SLA_TARGET)deadline_boosts++;
  }else{
   // The demand-normalized deficit is 1 - admitted/eligible; use cross products
   // to rank fractions *without floats* and without dividing by zero.
   // Age override above remains mandatory for starvation protection.
   int best_age=-1,best_turn=FLOORS+1;
   for(int turn=0;turn<FLOORS;turn++){
    int d=(rr_next+turn)%FLOORS,best=-1;
    for(int i=0;i<LANES;i++)if(phase[i]==3&&source_floor[i]==d)
     if(best<0||arrival_tick[i]<arrival_tick[best]||(arrival_tick[i]==arrival_tick[best]&&i<best))best=i;
    if(best<0)continue;
    int age=ticks-arrival_tick[best];
    int req=requested_by_silo[d],adm=issued_by_silo[d];
    int replace=chosen<0;
    if(!replace){int oldreq=requested_by_silo[chosen_domain],oldadm=issued_by_silo[chosen_domain];
      long long lhs=(long long)adm*oldreq,rhs=(long long)oldadm*req;
      replace=lhs<rhs||(lhs==rhs&&(age>best_age||(age==best_age&&turn<best_turn)));
    }
    if(replace){chosen=best;chosen_domain=d;best_age=age;best_turn=turn;}
   }
  }
  if(chosen>=0)fairness_selections++;
 }
 if(chosen<0)return;
 rr_next=(chosen_domain+1)%FLOORS;issued_by_silo[chosen_domain]++;
 if(fairness_policy==2)normalized_policy_admissions++;
 if(fairness_policy==3){sla_admissions++;if(ticks-arrival_tick[chosen]>SLA_TARGET)overdue_admissions++;}
 if(gate_status[chosen]==1){gate_admitted_possible++;if(ticks-gate_request_tick[chosen]>SLA_TARGET)gate_candidate_late_admissions++;}
 else if(gate_status[chosen]==2)gate_admitted_impossible++;
 else if(gate_status[chosen]==3)gate_admitted_unchecked++;
 waiting--;int delay=ticks-arrival_tick[chosen];if(delay>max_wait_ticks)max_wait_ticks=delay;
 int bucket=delay<HIST_LIMIT?delay:HIST_LIMIT-1;
 wait_hist[chosen_domain][bucket]++;wait_sum_by_silo[chosen_domain]+=delay;
 if(delay>wait_max_by_silo[chosen_domain])wait_max_by_silo[chosen_domain]=delay;
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
   if(ack_tick[i]>=ACK_TICKS){gate_on_ack(i);ack_seq[i]++;acks++;acknowledgements_by_silo[source_floor[i]]++;phase[i]=0;ack_tick[i]=0;}
  }
  else if(phase[i]==1){
   via_tick[i]++;
   if(via_tick[i]>=VIA_TICKS){
    if(kind[i]==2){gate_on_eligible(i);phase[i]=3;arrival_tick[i]=ticks;waiting++;requested_by_silo[source_floor[i]]++;}
    else {photon_hop(i,source_copper[i]&7,target_copper[i]&7);copper[i]=target_copper[i];phase[i]=via_tick[i]=progress[i]=0;hops[i]++;vias++;}
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
 // Causal, work-conserving service: only the first N oldest entries are serviced;
 // each receives exactly AGG_TICKS units of service; commits preserve FIFO order.
 // Both policies retain the same CAPACITY=8 and round-robin domain admission.
 int busy=qcount<service_channels?qcount:service_channels;
 if(busy>peak_busy_channels)peak_busy_channels=busy;
 channel_busy_ticks+=busy;
 for(int k=0;k<busy;k++){int i=queue[(qhead+k)%CAPACITY];agg_tick[i]++;}
 while(qcount>0){int i=queue[qhead];if(agg_tick[i]<AGG_TICKS)break;commit_head();}
 // Admit at most one candidate per tick, with bounded aggregate occupancy.
 admit_one();
 waiter_ticks+=waiting;if(waiting>max_waiting)max_waiting=waiting;
 for(int i=0;i<LANES;i++)if(phase[i]==3)waiting_ticks_by_silo[source_floor[i]]++;
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

// SHEET96 service policy; allows 1 original worker or 2 parallel logical workers.
// Test harness sets this before reset/stress; changing it mid-flight is not modeled.
__attribute__((export_name("set_service_channels"))) void set_service_channels(int n){service_channels=n==2?2:1;}
__attribute__((export_name("get_service_channels"))) int get_service_channels(void){return service_channels;}
SCALAR(get_peak_busy_channels,peak_busy_channels)
SCALAR(get_channel_busy_ticks,channel_busy_ticks)

// SHEET97 scoreboard: selections only, no manipulation of active routes or ACKs.
__attribute__((export_name("set_fairness_policy"))) void set_fairness_policy(int n){fairness_policy=n==3?3:(n==2?2:(n==1?1:0));}
__attribute__((export_name("get_fairness_policy"))) int get_fairness_policy(void){return fairness_policy;}
__attribute__((export_name("get_issued_silo"))) int get_issued_silo(int d){return d>=0&&d<FLOORS?issued_by_silo[d]:-999;}
SCALAR(get_fairness_age_overrides,fairness_age_overrides)
SCALAR(get_fairness_selections,fairness_selections)
__attribute__((export_name("get_fairness_age_limit"))) int get_fairness_age_limit(void){return FAIR_AGE_LIMIT;}

// SHEET98 report API; integer basis points avoid falsely equating raw service counts.
__attribute__((export_name("get_demand_silo"))) int get_demand_silo(int d){return d>=0&&d<FLOORS?requested_by_silo[d]:-999;}
__attribute__((export_name("get_waiting_lane_ticks_silo"))) int get_waiting_lane_ticks_silo(int d){return d>=0&&d<FLOORS?waiting_ticks_by_silo[d]:-999;}
__attribute__((export_name("get_ack_silo"))) int get_ack_silo(int d){return d>=0&&d<FLOORS?acknowledgements_by_silo[d]:-999;}
__attribute__((export_name("get_wait_sum_silo"))) int get_wait_sum_silo(int d){return d>=0&&d<FLOORS?wait_sum_by_silo[d]:-999;}
__attribute__((export_name("get_wait_max_silo"))) int get_wait_max_silo(int d){return d>=0&&d<FLOORS?wait_max_by_silo[d]:-999;}
__attribute__((export_name("get_pending_demand_silo"))) int get_pending_demand_silo(int d){return d>=0&&d<FLOORS?requested_by_silo[d]-issued_by_silo[d]:-999;}
__attribute__((export_name("get_admission_bps_silo"))) int get_admission_bps_silo(int d){return d>=0&&d<FLOORS?(requested_by_silo[d]>0?10000*issued_by_silo[d]/requested_by_silo[d]:10000):-999;}
__attribute__((export_name("get_p95_wait_silo"))) int get_p95_wait_silo(int d){
 if(d<0||d>=FLOORS)return -999;
 int count=issued_by_silo[d];if(count==0)return 0;
 int threshold=(95*count+99)/100,total=0;
 for(int k=0;k<HIST_LIMIT;k++){total+=wait_hist[d][k];if(total>=threshold)return k;}
 return HIST_LIMIT-1;
}
SCALAR(get_normalized_policy_admissions,normalized_policy_admissions)

// SHEET99 runtime SLA audit: target is objective, never advertised as a hard bound.
SCALAR(get_sla_target_ticks,SLA_TARGET)
SCALAR(get_sla_admissions,sla_admissions)
SCALAR(get_sla_overdue,overdue_admissions)
SCALAR(get_deadline_boosts,deadline_boosts)
__attribute__((export_name("get_current_oldest_wait"))) int get_current_oldest_wait(void){
 int oldest=0;for(int i=0;i<LANES;i++)if(phase[i]==3&&ticks-arrival_tick[i]>oldest)oldest=ticks-arrival_tick[i];return oldest;
}
__attribute__((export_name("get_overdue_pending"))) int get_overdue_pending(void){
 int n=0;for(int i=0;i<LANES;i++)if(phase[i]==3&&ticks-arrival_tick[i]>SLA_TARGET)n++;return n;
}

// SHEET100: optimistic capacity *necessary* conditions for a hypothetical
// simultaneously D8-eligible batch.  A positive result is NOT a guarantee.
// Service resources are shared and unavailable during 3D clearance holds.
__attribute__((export_name("get_hypothetical_admission_ceiling"))) int get_hypothetical_admission_ceiling(int horizon) {
 if(horizon < 0) return -1;
 // Best-case instantaneous initial fill of all CAPACITY slots, plus vacancies
 // opened by up to W workers finishing one transfer every AGG_TICKS.
 int bound=CAPACITY+service_channels*(horizon/AGG_TICKS);
 // This intentionally ignores the real admission <=1/tick limit: still safe,
 // if overly optimistic, as a necessary impossibility certificate.
 return bound;
}
__attribute__((export_name("get_hypothetical_commit_ceiling"))) int get_hypothetical_commit_ceiling(int horizon) {
 if(horizon<0) return -1;
 return service_channels*(horizon/AGG_TICKS);
}
__attribute__((export_name("get_hypothetical_ack_ceiling"))) int get_hypothetical_ack_ceiling(int horizon) {
 if(horizon<0) return -1;
 if(horizon<=ACK_TICKS)return 0;
 return service_channels*((horizon-ACK_TICKS)/AGG_TICKS);
}
__attribute__((export_name("get_burst_impossible_flags"))) int get_burst_impossible_flags(int eligible,int horizon) {
 if(eligible<0||eligible>100000||horizon<0||horizon>1000000)return -1;
 int flags=0;
 if(eligible>get_hypothetical_admission_ceiling(horizon))flags|=1;
 if(eligible>get_hypothetical_commit_ceiling(horizon))flags|=2;
 if(eligible>get_hypothetical_ack_ceiling(horizon))flags|=4;
 return flags;
}
__attribute__((export_name("get_burst_min_ack_ticks"))) int get_burst_min_ack_ticks(int eligible){
 if(eligible<0||eligible>100000)return -1;
 if(eligible==0)return 0;
 // Optimistic synchronized workers (no clearance, no queue admission cost).
 return ((eligible+service_channels-1)/service_channels)*AGG_TICKS+ACK_TICKS;
}
__attribute__((export_name("get_burst_min_commit_ticks"))) int get_burst_min_commit_ticks(int eligible){
 if(eligible<0||eligible>100000)return -1;
 return ((eligible+service_channels-1)/service_channels)*AGG_TICKS;
}
__attribute__((export_name("get_feasibility_model_version"))) int get_feasibility_model_version(void){return 100;}

// SHEET101 exported audit: gate_enabled is deliberately not reset by reset();
// a policy change applies at the next explicit new session, as for worker count.
__attribute__((export_name("set_gate_enabled"))) void set_gate_enabled(int v){gate_enabled=v?1:0;}
__attribute__((export_name("get_gate_enabled"))) int get_gate_enabled(void){return gate_enabled;}
__attribute__((export_name("get_gate_target_ticks"))) int get_gate_target_ticks(void){return SLA_TARGET;}
__attribute__((export_name("get_gate_status"))) int get_gate_status(int i){return i>=0&&i<LANES?gate_status[i]:-999;}
__attribute__((export_name("get_gate_lower_bound"))) int get_gate_lower_bound(int i){return i>=0&&i<LANES?gate_lower_bound_ticks[i]:-999;}
__attribute__((export_name("get_gate_request_tick"))) int get_gate_request_tick(int i){return i>=0&&i<LANES?gate_request_tick[i]:-999;}
SCALAR(get_gate_requests,gate_requests)
SCALAR(get_gate_possible,gate_possible)
SCALAR(get_gate_impossible,gate_impossible)
SCALAR(get_gate_unchecked,gate_unchecked)
SCALAR(get_gate_acks_possible,gate_acks_possible)
SCALAR(get_gate_acks_impossible,gate_acks_impossible)
SCALAR(get_gate_acks_unchecked,gate_acks_unchecked)
SCALAR(get_gate_late_possible,gate_late_possible)
SCALAR(get_gate_late_impossible,gate_late_impossible)
SCALAR(get_gate_late_unchecked,gate_late_unchecked)
SCALAR(get_gate_admitted_possible,gate_admitted_possible)
SCALAR(get_gate_admitted_impossible,gate_admitted_impossible)
SCALAR(get_gate_admitted_unchecked,gate_admitted_unchecked)
SCALAR(get_gate_candidate_late_admissions,gate_candidate_late_admissions)
__attribute__((export_name("get_gate_requests_silo"))) int get_gate_requests_silo(int d){return d>=0&&d<FLOORS?gate_request_by_silo[d]:-999;}
__attribute__((export_name("get_gate_possible_silo"))) int get_gate_possible_silo(int d){return d>=0&&d<FLOORS?gate_possible_by_silo[d]:-999;}
__attribute__((export_name("get_gate_impossible_silo"))) int get_gate_impossible_silo(int d){return d>=0&&d<FLOORS?gate_impossible_by_silo[d]:-999;}
__attribute__((export_name("get_gate_late_silo"))) int get_gate_late_silo(int d){return d>=0&&d<FLOORS?gate_late_by_silo[d]:-999;}
__attribute__((export_name("get_gate_model_version"))) int get_gate_model_version(void){return 101;}