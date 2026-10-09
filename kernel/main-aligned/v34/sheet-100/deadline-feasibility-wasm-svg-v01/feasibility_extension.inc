// SHEET100 appendix: append to SHEET99 kernel.c (requires service_channels,
// AGG_TICKS, ACK_TICKS and CAPACITY from parent kernel).
// All ceilings are intentionally optimistic NECESSARY conditions, not guarantees.
__attribute__((export_name("get_hypothetical_admission_ceiling"))) int get_hypothetical_admission_ceiling(int horizon) {
 if(horizon < 0) return -1;
 int bound=CAPACITY+service_channels*(horizon/AGG_TICKS);
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
 return ((eligible+service_channels-1)/service_channels)*AGG_TICKS+ACK_TICKS;
}
__attribute__((export_name("get_burst_min_commit_ticks"))) int get_burst_min_commit_ticks(int eligible){
 if(eligible<0||eligible>100000)return -1;
 return ((eligible+service_channels-1)/service_channels)*AGG_TICKS;
}
__attribute__((export_name("get_feasibility_model_version"))) int get_feasibility_model_version(void){return 100;}
