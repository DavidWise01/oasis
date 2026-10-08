// SHEET 90 :: 8 |0| 8 |0| 8 |0| 8 :: eight toroidal floors x 9 rings
// Freestanding wasm32 state machine; symbolic topology, not electromagnetic physics.
#define LANES 120
#define FLOORS 8
#define TOROIDS 9
#define COPPER 11
#define OCTETS 4
#define SCALE 1000000
#define VIA_TICKS 24
static int floor_no[LANES],ring[LANES],copper[LANES],bank[LANES],cell[LANES];
static int progress[LANES],speed[LANES],phase[LANES],via_tick[LANES],hops[LANES];
static int source_floor[LANES],target_floor[LANES],source_copper[LANES],target_copper[LANES];
static int source_bank[LANES],target_bank[LANES],kind[LANES]; // kind 1 copper via; 2 floor via
static int ticks=0, orbits=0, vias=0, floor_vias=0, zero_gates=0;
static int reflect(int n,int limit,int sign){int candidate=n+sign;return candidate<0?1:(candidate>=limit?limit-2:candidate);}
__attribute__((export_name("reset"))) void reset(void){
 ticks=orbits=vias=floor_vias=zero_gates=0;
 for(int i=0;i<LANES;i++){
  floor_no[i]=i%FLOORS;ring[i]=i%TOROIDS;copper[i]=i%COPPER;
  bank[i]=(i/8)%OCTETS;cell[i]=i%8;
  progress[i]=(i*7919)%SCALE;speed[i]=3800+(i*83)%5800;
  phase[i]=via_tick[i]=hops[i]=kind[i]=0;
  source_floor[i]=target_floor[i]=floor_no[i];
  source_copper[i]=target_copper[i]=copper[i];
  source_bank[i]=target_bank[i]=bank[i];
 }
}
__attribute__((export_name("step"))) void step(void){
 ticks++;
 for(int i=0;i<LANES;i++){
  if(phase[i]==0){
   progress[i]+=speed[i];
   if(progress[i]>=SCALE){
    progress[i]=SCALE;orbits++;phase[i]=1;via_tick[i]=0;
    source_floor[i]=target_floor[i]=floor_no[i];
    source_copper[i]=target_copper[i]=copper[i];
    source_bank[i]=target_bank[i]=bank[i];
    kind[i]=(hops[i]%3==2)?2:1;
    if(kind[i]==1){target_copper[i]=reflect(copper[i],COPPER,(i&1)?-1:1);}
    else{
     target_floor[i]=reflect(floor_no[i],FLOORS,(i&1)?-1:1);
     target_bank[i]=(bank[i]+1)%OCTETS;
    }
   }
  }else{
   via_tick[i]++;
   if(via_tick[i]>=VIA_TICKS){
    floor_no[i]=target_floor[i];copper[i]=target_copper[i];
    if(kind[i]==2){floor_vias++;if(source_bank[i]<3)zero_gates++;}
    bank[i]=target_bank[i];
    phase[i]=via_tick[i]=progress[i]=0;
    hops[i]++;vias++;
   }
  }
 }
}
#define GET(name,data) __attribute__((export_name(#name))) int name(int i){return i>=0&&i<LANES?data[i]:-999;}
GET(get_floor,floor_no) GET(get_ring,ring) GET(get_copper,copper)
GET(get_bank,bank) GET(get_cell,cell) GET(get_progress,progress)
GET(get_speed,speed) GET(get_phase,phase) GET(get_via_tick,via_tick)
GET(get_source_floor,source_floor) GET(get_target_floor,target_floor)
GET(get_source_copper,source_copper) GET(get_target_copper,target_copper)
GET(get_source_bank,source_bank) GET(get_target_bank,target_bank)
GET(get_kind,kind) GET(get_hops,hops)
__attribute__((export_name("get_ticks"))) int get_ticks(void){return ticks;}
__attribute__((export_name("get_orbits"))) int get_orbits(void){return orbits;}
__attribute__((export_name("get_vias"))) int get_vias(void){return vias;}
__attribute__((export_name("get_floor_vias"))) int get_floor_vias(void){return floor_vias;}
__attribute__((export_name("get_zero_gates"))) int get_zero_gates(void){return zero_gates;}
__attribute__((export_name("get_lanes"))) int get_lanes(void){return LANES;}
__attribute__((export_name("get_floors"))) int get_floors(void){return FLOORS;}
__attribute__((export_name("get_toroids"))) int get_toroids(void){return TOROIDS;}
__attribute__((export_name("get_copper_layers"))) int get_copper_layers(void){return COPPER;}
__attribute__((export_name("get_via_ticks"))) int get_via_ticks(void){return VIA_TICKS;}
__attribute__((export_name("get_octet_banks"))) int get_octet_banks(void){return OCTETS;}
