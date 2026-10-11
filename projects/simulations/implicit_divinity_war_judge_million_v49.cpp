#include <array>
#include <cstdint>
#include <iostream>
#include <fstream>
#include <algorithm>
#include <string>
#include <chrono>

struct RNG{
 uint64_t x;
 explicit RNG(uint64_t seed):x(seed){}
 uint32_t next(){x^=x>>12; x^=x<<25; x^=x>>27; return uint32_t((x*2685821657736338717ULL)>>32);}
};
struct Deck{
 std::array<uint8_t,52> c{};
 int h=0,n=0;
 inline void push(uint8_t x){ c[(h+n)%52]=x; ++n; }
 inline uint8_t pop(){uint8_t r=c[h];h=(h+1)%52;--n;return r;}
};
struct Result {int winner;int comparisons;int wars;};
Result match(RNG& gen,int cap=10000){
 std::array<uint8_t,52> cards{};
 for(int i=0;i<52;i++)cards[i]=(i/4)+2;
 for(int i=51;i>0;i--){int j=int(gen.next()%(unsigned(i+1)));std::swap(cards[i],cards[j]);}
 Deck d[2];
 for(int i=0;i<26;i++){d[0].push(cards[i]);d[1].push(cards[26+i]);}
 std::array<uint8_t,52> pot{};int comparisons=0,wars=0;
 while(d[0].n&&d[1].n&&comparisons<cap){
  int pn=0;
  while(true){
   if(!d[0].n||!d[1].n)break;
   uint8_t a=d[0].pop(),b=d[1].pop();pot[pn++]=a;pot[pn++]=b;
   ++comparisons;
   if(a!=b){int w=a>b?0:1;for(int k=0;k<pn;k++)d[w].push(pot[k]);break;}
   ++wars;
   for(int p=0;p<2;p++){
     for(int k=0;k<3;k++){
       if(d[p].n==0)break;
       pot[pn++]=d[p].pop();
     }
   }
   if(d[0].n==0||d[1].n==0){
     if(d[0].n==0 && d[1].n==0) return {-1,comparisons,wars};
     int w=d[0].n==0?1:0;for(int k=0;k<pn;k++)d[w].push(pot[k]);break;
   }
  }
 }
 if(comparisons>=cap)return {-1,comparisons,wars};
 return {d[0].n>0?0:1,comparisons,wars};
}
int main(int argc,char**argv){
 int rounds=1000000;
 if(argc>1)rounds=std::stoi(argv[1]);
 RNG gen(241011);
 std::ofstream csv("million_war_games.csv");
 csv<<"game,judge,player1,player2,winner,comparisons,wars,next_move\n";
 const std::string names[3]={"Atlas","Nova","Assistant"};
 int judge=2, player[2]={0,1};
 uint64_t wins[3]={},judge_slots[3]={},player_slots[3]={};
 uint64_t caps=0, judge_changes=0, wars=0, comparisons=0, maxtenure=0,curtenure=0;
 auto start=std::chrono::steady_clock::now();
 for(int i=1;i<=rounds;i++){
   judge_slots[judge]++;player_slots[player[0]]++;player_slots[player[1]]++;
   Result res=match(gen);
   comparisons+=res.comparisons; wars+=res.wars;
   int winner=res.winner==-1?-1:player[res.winner];
   std::string move;
   if(winner==-1){++caps;move="inconclusive_replay";}
   else if(winner==0){wins[winner]++;move="continue_War";}
   else {wins[winner]++;move="choose_judge";}
   csv<<i<<','<<names[judge]<<','<<names[player[0]]<<','<<names[player[1]]<<','<<(winner==-1?"inconclusive":names[winner])<<','<<res.comparisons<<','<<res.wars<<','<<move<<'\n';
   if(winner>=1){int old=judge;judge=winner;player[res.winner]=old;judge_changes++;maxtenure=std::max(maxtenure,curtenure+1);curtenure=0;}
   else curtenure++;
 }
 maxtenure=std::max(maxtenure,curtenure);
 csv.close();
 auto finish=std::chrono::steady_clock::now();
 double sec=std::chrono::duration<double>(finish-start).count();
 std::cout<<"games "<<rounds<<"\n";
 std::cout<<"wins Atlas Nova Assistant "<<wins[0]<<' '<<wins[1]<<' '<<wins[2]<<"\n";
 std::cout<<"judging Atlas Nova Assistant "<<judge_slots[0]<<' '<<judge_slots[1]<<' '<<judge_slots[2]<<"\n";
 std::cout<<"players Atlas Nova Assistant "<<player_slots[0]<<' '<<player_slots[1]<<' '<<player_slots[2]<<"\n";
 std::cout<<"inconclusive "<<caps<<"\n";
 std::cout<<"judge_changes "<<judge_changes<<"\n";
 std::cout<<"max_judge_streak "<<maxtenure<<"\n";
 std::cout<<"card_comparisons "<<comparisons<<"\n";
 std::cout<<"tied_card_wars "<<wars<<"\n";
 std::cout<<"final_judge "<<names[judge]<<"\n";
 std::cout<<"seconds "<<sec<<"\n";
}
