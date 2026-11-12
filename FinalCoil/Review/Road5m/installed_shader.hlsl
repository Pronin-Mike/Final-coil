// Author-owned, world-space procedural PBR. World position/height in centimeters.
// No periodic UV tile. Large domain-warped patches and cell-randomized detail.
struct GroundFns {
 float hash(float2 p) { float3 q=frac(float3(p.xyx)*.1031);q+=dot(q,q.yzx+33.33);return frac((q.x+q.y)*q.z); }
 float noise(float2 p) {float2 i=floor(p),f=frac(p);f=f*f*(3-2*f);return lerp(lerp(hash(i),hash(i+float2(1,0)),f.x),lerp(hash(i+float2(0,1)),hash(i+1),f.x),f.y);}
 float fbm(float2 p) {float v=0,a=.57;[unroll]for(int i=0;i<4;i++){v+=a*noise(p);p=mul(float2x2(.8,-.6,.6,.8),p)*2.13+17.13;a*=.47;}return v;}
 float segment(float2 p,float2 a,float2 b) {float2 v=b-a;return length(p-a-v*saturate(dot(p-a,v)/dot(v,v)));}
 float roadDist(float2 p) {float d=1e9; d=min(d,segment(p,float2(-28333.3320,-132666.6670),float2(-16666.6680,-89999.9996)));
d=min(d,segment(p,float2(-16666.6679,-89999.9996),float2(-1333.3321,-43333.3337)));
d=min(d,segment(p,float2(-1333.3327,-43333.3334),float2(-0.0006,-20000.0000)));
d=min(d,segment(p,float2(-0.0000,-20000.0000),float2(0.0000,0.0000)));
d=min(d,segment(p,float2(0.0003,-0.0001),float2(2639.9997,15000.0001)));
d=min(d,segment(p,float2(2640.0001,15000.0000),float2(3402.6666,19333.3334)));
d=min(d,segment(p,float2(3402.6672,19333.3332),float2(7333.3328,41666.6668)));
d=min(d,segment(p,float2(7333.3344,41666.6663),float2(25333.3323,86666.6671)));
d=min(d,segment(p,float2(25333.3321,86666.6668),float2(29666.6679,127666.6665)));
d=min(d,segment(p,float2(29666.6664,127666.6666),float2(21666.6669,168333.3334)));
d=min(d,segment(p,float2(21666.6656,168333.3328),float2(5666.6678,204000.0005)));
d=min(d,segment(p,float2(5666.6653,203999.9998),float2(-666.6653,252666.6668)));
d=min(d,segment(p,float2(-666.6666,252666.6666),float2(10000.0000,270000.0000)));
d=min(d,segment(p,float2(10000.0000,270000.0000),float2(32333.3333,273333.3334)));
d=min(d,segment(p,float2(32333.3334,273333.3334),float2(55333.3333,264333.3333)));
d=min(d,segment(p,float2(55333.3333,264333.3333),float2(80000.0000,264666.6667)));
d=min(d,segment(p,float2(80000.0001,264666.6668),float2(98333.3332,249999.9999)));
d=min(d,segment(p,float2(98333.3328,249999.9998),float2(105666.6672,227000.0002)));
d=min(d,segment(p,float2(3402.6666,19333.3334),float2(31000.0001,34999.9999)));
d=min(d,segment(p,float2(31000.0000,35000.0001),float2(60333.3334,47999.9999)));
d=min(d,segment(p,float2(60333.3332,48000.0001),float2(80000.0001,69999.9999)));
d=min(d,segment(p,float2(80000.0002,69999.9999),float2(97999.9998,101333.3335)));
d=min(d,segment(p,float2(97999.9998,101333.3335),float2(109333.3335,114333.3332)));
d=min(d,segment(p,float2(109333.3334,114333.3333),float2(118666.6666,118333.3334)));
d=min(d,segment(p,float2(2639.9999,14999.9998),float2(-1333.3333,16666.6669)));
d=min(d,segment(p,float2(-1333.3333,16666.6667),float2(-4333.3333,16333.3333)));
d=min(d,segment(p,float2(-4333.3333,16333.3333),float2(-5666.6667,15666.6667)));
d=min(d,segment(p,float2(-5666.6667,15666.6666),float2(-7500.0000,16300.0001))); return d;}
 float blade(float2 p,float scale,float seed) {
  p=p/scale;float2 cell=floor(p),v=frac(p)-.5;float h=hash(cell+seed);float a=h*6.283;
  v-=(float2(hash(cell+seed+12),hash(cell+seed+44))-.5)*.7;
  v*=lerp(.72,1.62,hash(cell+seed+9));
  v=mul(float2x2(cos(a),-sin(a),sin(a),cos(a)),v);
  float bent=v.x+lerp(.04,.24,h)*sin(v.y*(2+h*4)+h*6);float width=lerp(.025,.060,h)*(1-smoothstep(-.2,.44,v.y));
  float aa=max(.012,fwidth(bent)*.7);
  return (1-smoothstep(width-aa,width+aa,abs(bent)))*(1-smoothstep(.22,.44,abs(v.y)))*smoothstep(.12,.3,h);
 }
 float pebble(float2 p,out float random) {
  p/=7.7;float2 cell=floor(p);float best=1,hh=0;
  [unroll]for(int x=-1;x<=1;x++)[unroll]for(int y=-1;y<=1;y++){
   float2 c=cell+float2(x,y);float h=hash(c+41);float2 pt=c+float2(hash(c+17),hash(c+93));float2 v=p-pt;
   float a=h*6.283;v=mul(float2x2(cos(a),-sin(a),sin(a),cos(a)),v);float dist=length(v*float2(1,1.5));
   float r=lerp(.07,.23,h);float b=(1-smoothstep(r*.55,r,dist))*step(.965,h);
   if(b>1-best){best=1-b;hh=h;}
  }random=hh;return 1-best;
 }
float4 villageRoad(float2 p){float best=1e9,d=1e9,w=350,dd;dd=segment(p,float2(-28333.33196,-132666.66704),float2(-16666.66804,-89999.99963));if(dd-350.00000<best){best=dd-350.00000;d=dd;w=350.00000;}dd=segment(p,float2(-16666.66792,-89999.99959),float2(-1333.33208,-43333.33374));if(dd-350.00000<best){best=dd-350.00000;d=dd;w=350.00000;}dd=segment(p,float2(-1333.33272,-43333.33337),float2(-0.00061,-19999.99997));if(dd-350.00000<best){best=dd-350.00000;d=dd;w=350.00000;}dd=segment(p,float2(-0.00000,-20000.00000),float2(0.00000,0.00000));if(dd-350.00000<best){best=dd-350.00000;d=dd;w=350.00000;}dd=segment(p,float2(0.00033,-0.00006),float2(2639.99967,15000.00006));if(dd-350.00000<best){best=dd-350.00000;d=dd;w=350.00000;}dd=segment(p,float2(2640.00009,14999.99998),float2(3402.66657,19333.33335));if(dd-350.00000<best){best=dd-350.00000;d=dd;w=350.00000;}dd=segment(p,float2(3402.66715,19333.33325),float2(7333.33285,41666.66675));if(dd-350.00000<best){best=dd-350.00000;d=dd;w=350.00000;}dd=segment(p,float2(7333.33436,41666.66625),float2(25333.33230,86666.66708));if(dd-350.00000<best){best=dd-350.00000;d=dd;w=350.00000;}dd=segment(p,float2(25333.33207,86666.66680),float2(29666.66793,127666.66653));if(dd-350.00000<best){best=dd-350.00000;d=dd;w=350.00000;}dd=segment(p,float2(29666.66640,127666.66661),float2(21666.66693,168333.33339));if(dd-350.00000<best){best=dd-350.00000;d=dd;w=350.00000;}dd=segment(p,float2(21666.66556,168333.33284),float2(5666.66778,204000.00050));if(dd-350.00000<best){best=dd-350.00000;d=dd;w=350.00000;}dd=segment(p,float2(5666.66530,203999.99982),float2(-666.66530,252666.66684));if(dd-350.00000<best){best=dd-350.00000;d=dd;w=350.00000;}dd=segment(p,float2(-666.66663,252666.66664),float2(9999.99996,270000.00002));if(dd-350.00000<best){best=dd-350.00000;d=dd;w=350.00000;}dd=segment(p,float2(10000.00001,269999.99997),float2(32333.33333,273333.33337));if(dd-350.00000<best){best=dd-350.00000;d=dd;w=350.00000;}dd=segment(p,float2(32333.33336,273333.33341),float2(55333.33330,264333.33326));if(dd-350.00000<best){best=dd-350.00000;d=dd;w=350.00000;}dd=segment(p,float2(55333.33333,264333.33333),float2(80000.00000,264666.66667));if(dd-350.00000<best){best=dd-350.00000;d=dd;w=350.00000;}dd=segment(p,float2(80000.00011,264666.66680),float2(98333.33322,249999.99986));if(dd-350.00000<best){best=dd-350.00000;d=dd;w=350.00000;}dd=segment(p,float2(98333.33277,249999.99982),float2(105666.66723,227000.00018));if(dd-350.00000<best){best=dd-350.00000;d=dd;w=350.00000;}dd=segment(p,float2(3402.66662,19333.33342),float2(31000.00005,34999.99991));if(dd-300.00000<best){best=dd-300.00000;d=dd;w=300.00000;}dd=segment(p,float2(30999.99996,35000.00010),float2(60333.33338,47999.99990));if(dd-300.00000<best){best=dd-300.00000;d=dd;w=300.00000;}dd=segment(p,float2(60333.33324,48000.00008),float2(80000.00009,69999.99992));if(dd-300.00000<best){best=dd-300.00000;d=dd;w=300.00000;}dd=segment(p,float2(80000.00024,69999.99986),float2(97999.99976,101333.33347));if(dd-300.00000<best){best=dd-300.00000;d=dd;w=300.00000;}dd=segment(p,float2(97999.99981,101333.33350),float2(109333.33352,114333.33317));if(dd-300.00000<best){best=dd-300.00000;d=dd;w=300.00000;}dd=segment(p,float2(109333.33336,114333.33327),float2(118666.66664,118333.33339));if(dd-300.00000<best){best=dd-300.00000;d=dd;w=300.00000;}dd=segment(p,float2(2639.99992,14999.99981),float2(-1333.33326,16666.66685));if(dd-200.00000<best){best=dd-200.00000;d=dd;w=200.00000;}dd=segment(p,float2(-1333.33334,16666.66674),float2(-4333.33332,16333.33326));if(dd-200.00000<best){best=dd-200.00000;d=dd;w=200.00000;}dd=segment(p,float2(-4333.33332,16333.33330),float2(-5666.66668,15666.66670));if(dd-200.00000<best){best=dd-200.00000;d=dd;w=200.00000;}dd=segment(p,float2(-5666.66673,15666.66662),float2(-7499.99997,16300.00008));if(dd-200.00000<best){best=dd-200.00000;d=dd;w=200.00000;}return float4(d,w,0,0);}
float mainRoadDistance(float2 p){float d=1e9;d=min(d,segment(p,float2(-28333.331964,-132666.667041),float2(-16666.668036,-89999.999626)));d=min(d,segment(p,float2(-16666.667916,-89999.999590),float2(-1333.332084,-43333.333744)));d=min(d,segment(p,float2(-1333.332723,-43333.333368),float2(-0.000611,-19999.999965)));d=min(d,segment(p,float2(-0.000000,-20000.000000),float2(0.000000,0.000000)));d=min(d,segment(p,float2(0.000328,-0.000058),float2(2639.999672,15000.000058)));d=min(d,segment(p,float2(2640.000095,14999.999983),float2(3402.666572,19333.333350)));d=min(d,segment(p,float2(3402.667155,19333.333247),float2(7333.332845,41666.666753)));d=min(d,segment(p,float2(7333.334365,41666.666254),float2(25333.332302,86666.667079)));d=min(d,segment(p,float2(25333.332072,86666.666800),float2(29666.667928,127666.666533)));d=min(d,segment(p,float2(29666.666400,127666.666614),float2(21666.666934,168333.333386)));d=min(d,segment(p,float2(21666.665558,168333.332836),float2(5666.667776,204000.000498)));d=min(d,segment(p,float2(5666.665301,203999.999822),float2(-666.665301,252666.666844)));d=min(d,segment(p,float2(-666.666627,252666.666642),float2(9999.999960,270000.000024)));return d;}
}; GroundFns g;
float2 p=P.xy;
float footprint=max(length(ddx(p)),length(ddy(p)));
float microFade=1-smoothstep(2.0,14.0,footprint);
float2 warp=float2(g.fbm(p/5700+31),g.fbm(p/5100-27))-.5;
float macro=g.fbm(p/max(MacroScale,100)+warp*2.4);
float patch=g.fbm(p/470+warp*4.3);
float small=g.fbm(p/62+float2(31,9));
float grain=g.noise(p/1.7)*microFade+.5*(1-microFade);
float slope=1-saturate(VN.z);
float dry=saturate(Biome.a*.65+smoothstep(250,1200,P.z)*.35+smoothstep(.008,.075,slope)*.6);
float wet=saturate(Biome.g*Wetness*(.48+.6*patch));
float lake=Biome.b;
float level=WaterLevel;
float shore=lake*(1-smoothstep(level+35,level+290,P.z));
float submerged=lake*(1-smoothstep(level-45,level+15,P.z));
wet=max(wet,shore*.92);
float forest=saturate(Biome.r*ForestAmount + (macro-.48)*.18*Biome.r*(1-Biome.r));
float compact=saturate(max(Use.r,max(Use.g*.92,Use.b*.78)));
if(SurfaceKind>0.5 && SurfaceKind<3.5)compact=max(compact,.96);
float grass=smoothstep(.30,.65,macro+.19*patch+.08*small-dry*.19);
grass*=1-saturate(compact*.95+shore*.94+submerged+forest*.9);
float moss=forest*wet*smoothstep(.30,.58,patch)*.8;
float rut=0;
[branch]if(Use.r>.03 || (SurfaceKind>.5 && SurfaceKind<1.5)){
 float d=g.roadDist(p);rut=(1-smoothstep(18,40,abs(d-105)))*smoothstep(.1,.5,Use.r);
}
float puddle=smoothstep(.60,.91,Biome.g)*smoothstep(.43,.62,patch)*(.3+.7*compact);
wet=saturate(max(wet,puddle*.92)+rut*Biome.g*.3);
float3 soil=lerp(float3(.095,.065,.038),float3(.205,.154,.092),dry*.65+macro*.25);
soil*=lerp(.72,1.23,small)*lerp(.90,1.08,grain);
float3 grassCol=lerp(float3(.048,.083,.019),float3(.175,.154,.054),saturate(dry*.48+patch*.38));
grassCol*=lerp(.65,1.24,small);
float3 color=lerp(soil,grassCol,grass);
float3 litter=lerp(float3(.034,.025,.014),float3(.092,.061,.028),patch);
color=lerp(color,litter,forest*(1-compact*.87));
color=lerp(color,float3(.035,.055,.018)*(small+.55),moss);
float beach=shore*(1-forest*.6);
color=lerp(color,lerp(float3(.12,.101,.068),float3(.19,.16,.105),patch),beach*.75);
color=lerp(color,float3(.072,.058,.039)*(small*.4+.7),submerged*.75);
color=lerp(color,soil*.92,compact*.77);
// Random orientation and curved stems break a repeated grass/needle stamp.
float stems=saturate(g.blade(p,9.3,2)+g.blade(p+7.3,6.8,19)+g.blade(p-13.7,12.7,63))*microFade;
float dead=g.blade(p+31,9.8,37)*microFade;
float needles=saturate(g.blade(p+91,4.4,87)+g.blade(p-41,6.2,97))*microFade;
float2 leafCell=floor(p/14.3),leafV=frac(p/14.3)-.5;
float leafRandom=g.hash(leafCell+19),leafAngle=leafRandom*6.283;
leafV=mul(float2x2(cos(leafAngle),-sin(leafAngle),sin(leafAngle),cos(leafAngle)),leafV);
float leaf=(1-smoothstep(.18,.25,length(leafV*float2(1.7,.85))))*step(.64,leafRandom)*microFade;
color=lerp(color,grassCol*lerp(1.2,1.7,patch),stems*grass*.93);
color=lerp(color,float3(.22,.17,.082),dead*grass*.28);
color=lerp(color,float3(.15,.10,.043),needles*forest*(1-compact)*.65);
float3 leafColor=lerp(float3(.10,.052,.016),float3(.24,.16,.055),leafRandom)*(1-.28*exp(-abs(leafV.x)*180));
color=lerp(color,leafColor,leaf*forest*(1-compact));
float stoneRandom;float stone=g.pebble(p,stoneRandom)*microFade;
float gravel=stone*(1-forest*.7)*(1-grass*.8)*GravelAmount;
color=lerp(color,lerp(float3(.13,.12,.10),float3(.29,.27,.23),stoneRandom),gravel);
color*=lerp(1,.43,wet*.83);
color*=1-rut*.11;
float height=(g.fbm(p/6)*.12+grain*.035+gravel*.45+stems*grass*.085+needles*forest*.055+leaf*.09*forest)*microFade;
height-=rut*.6;
float3 dpdx=ddx(P),dpdy=ddy(P),r1=cross(dpdy,VN),r2=cross(VN,dpdx);
float det=dot(dpdx,r1);
float3 gradient=(ddx(height)*r1+ddy(height)*r2)/(abs(det)>.000001?det:1);
GroundNormal=normalize(VN-gradient*NormalStrength*.5);
Roughness=clamp(lerp(.91,.38,wet)-puddle*.12+grass*.04-gravel*.05,.22,.98);
AO=clamp(.91+grain*.09-grass*.08-forest*.05,.72,1);
if(P.x>-7200.000000 && P.x<20174.668939 && P.y>-47374.798994 && P.y<58234.505365){
// Strictly regional: caller tests the current extreme-house rectangle first.
float4 rd=g.villageRoad(P.xy);
// VILLAGE_ROAD_5M: 5m carriageway, 0.5-1m shoulders on each side.
float dist=rd.x, width=rd.y-(g.mainRoadDistance(P.xy)<=rd.x+1?100:0);
// STOP01_LAYBY: one-sided 3m widening, 12m standing length and 12m tapers.
float stopLong=1-smoothstep(600,1800,abs(P.y));
float stopSide=smoothstep(-30,80,P.x);
width+=300*stopLong*stopSide;

float irregular=clamp((g.fbm(P.xy/330+warp*1.8)-.5)*90,-25,25);
float shoulder=1-smoothstep(width,width+75+irregular,dist);
float worn=shoulder*smoothstep(.30,.62,macro+.15*patch);
float sparse=1-smoothstep(-30,170,dist-width-irregular*.45);
float greens=saturate(.68+.38*macro+.20*wet-dry*.32);
greens*=smoothstep(.21,.42,patch+.15*macro);
float3 field=lerp(soil*.95,grassCol*1.05,greens);
float3 usedSoil=soil*lerp(.88,1.04,patch);
float lane=(1-smoothstep(28,64,abs(dist-105)));
float firmness=smoothstep(.28,.62,g.fbm(P.xy/820+17));
float marks=lane*(.24+.76*wet)*(.18+.82*firmness);
usedSoil*=1-marks*lerp(.045,.22,wet);
usedSoil+=lane*(1-wet)*(.012+.010*firmness);
float center=(1-smoothstep(35,72,dist))*smoothstep(.36,.68,macro+.15*small)*(.14+.24*wet);
usedSoil=lerp(usedSoil,grassCol*.92,center);
float edge=exp(-pow((dist-width-28)/38,2));
usedSoil=lerp(usedSoil,soil*1.08,smoothstep(width-5,width+35,dist)*.6);
float chips=smoothstep(.83,.95,g.noise(P.xy/3.7))*edge*microFade;
usedSoil=lerp(usedSoil,float3(.20,.185,.145)*(grain*.3+.8),chips*.33);
float3 nextColor=lerp(field,usedSoil,shoulder);
// Keep existing footpath controls as readable, gently frayed worn strips.
nextColor=lerp(nextColor,soil*.88,Use.g*.80);
float nextRough=lerp(.93,lerp(.90,.40,wet)-marks*.035,shoulder);
float edgeBlend=smoothstep(0,250,P.x-float4(-7200.000000,-47374.798994,20174.668939,58234.505365).x)*smoothstep(0,250,float4(-7200.000000,-47374.798994,20174.668939,58234.505365).z-P.x)*smoothstep(0,250,P.y-float4(-7200.000000,-47374.798994,20174.668939,58234.505365).y)*smoothstep(0,250,float4(-7200.000000,-47374.798994,20174.668939,58234.505365).w-P.y);
float protect=(1-smoothstep(.04,.34,Use.b))*(1-smoothstep(.02,.18,Biome.r));
float mixWeight=edgeBlend*protect;
// STOP01_WAITING: 6.2 x 8m gravel apron, separated from the carriageway.
float stopApron=(1-smoothstep(0,24,max(780-P.x,P.x-1400)))*(1-smoothstep(385,415,abs(P.y)));
float stopAccess=(1-smoothstep(70,100,abs(P.y)))*(1-smoothstep(0,24,max(480-P.x,P.x-820)));
float stopWait=max(stopApron,stopAccess);
float stopGrain=g.noise(P.xy/3.2);
float3 stopGravel=float3(.24,.22,.17)*(.86+.28*stopGrain);
nextColor=lerp(nextColor,stopGravel,stopWait);
float stopBayWeight=stopLong*stopSide*(1-smoothstep(width-20,width+80,dist));
color=lerp(color,nextColor,max(mixWeight,max(stopWait,stopBayWeight)));
Roughness=lerp(Roughness,nextRough,mixWeight);
AO=lerp(AO,.96,mixWeight*shoulder);

}
return max(color*Tint,0.002);
