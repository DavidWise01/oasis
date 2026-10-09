/* SHEET 102: Dot-photon (one dot = one carrier occurrence per logical tick)
 * State dimension 2^3=8. Every successful jump applies an invertible 8x8
 * permutation matrix, e_{j} -> e_{j xor (source xor destination)}.
 * Networking edge cost is nonnegative and independent from tick count.
 * This is a symbolic state machine, not a model of physical photons.
 */
#define N 8
static int states[N];
static int current, destination, tick, cumulative_cost, hops;
static int last_from, last_to;

static int connected(int a,int b){
  if(a<0||a>=N||b<0||b>=N||a==b) return 0;
  if(((a+1)&7)==b || ((b+1)&7)==a) return 1;
  return (a^b)==4; /* opposite vertices are chord-linked */
}
static int edge_cost(int a,int b){
  if(!connected(a,b)) return -1;
  int lo=a<b?a:b, hi=a>b?a:b;
  return 1+((lo*3+hi*5)%4); /* cost 1..4, not duration in ticks */
}
__attribute__((export_name("get_edge_cost"))) int get_edge_cost(int a,int b){return edge_cost(a,b);}
__attribute__((export_name("reset"))) int reset(int source,int target){
  if(source<0||source>=N||target<0||target>=N) return -1;
  current=source;destination=target;tick=0;hops=0;cumulative_cost=0;
  last_from=-1;last_to=-1;
  for(int i=0;i<N;i++) states[i]=i+1;
  return 0;
}
__attribute__((export_name("set_target"))) int set_target(int target){
  if(target<0||target>=N)return -1;
  destination=target;return 0;
}
__attribute__((export_name("get_state"))) int get_state(int i){return i>=0&&i<N?states[i]:-999;}
__attribute__((export_name("get_domain"))) int get_domain(void){return current;}
__attribute__((export_name("get_target"))) int get_target(void){return destination;}
__attribute__((export_name("get_tick"))) int get_tick(void){return tick;}
__attribute__((export_name("get_hops"))) int get_hops(void){return hops;}
__attribute__((export_name("get_cost"))) int get_cost(void){return cumulative_cost;}
__attribute__((export_name("get_last_from"))) int get_last_from(void){return last_from;}
__attribute__((export_name("get_last_to"))) int get_last_to(void){return last_to;}
__attribute__((export_name("get_dimension"))) int get_dimension(void){return N;}
__attribute__((export_name("advance"))) int advance(void){
  if(current==destination) return 0;
  int dist[N],used[N];
  for(int i=0;i<N;i++){dist[i]=100000;used[i]=0;}
  dist[destination]=0;
  for(int k=0;k<N;k++){
    int u=-1;
    for(int i=0;i<N;i++)if(!used[i]&&(u<0||dist[i]<dist[u]||(dist[i]==dist[u]&&i<u)))u=i;
    if(u<0||dist[u]==100000)break;
    used[u]=1;
    for(int v=0;v<N;v++){
      int c=edge_cost(u,v);
      if(c>0 && dist[u]+c<dist[v])dist[v]=dist[u]+c;
    }
  }
  int next=-1,best=100000;
  for(int v=0;v<N;v++){
    int c=edge_cost(current,v);
    if(c<0)continue;
    int cost=c+dist[v];
    if(cost<best||(cost==best&&(next<0||v<next))){best=cost;next=v;}
  }
  if(next<0||best>=100000)return -1;
  int scratch[N], mask=current^next;
  for(int i=0;i<N;i++)scratch[i^mask]=states[i];
  for(int i=0;i<N;i++)states[i]=scratch[i];
  cumulative_cost+=edge_cost(current,next);
  last_from=current;last_to=next;current=next;
  tick++;hops++;
  return 1;
}
