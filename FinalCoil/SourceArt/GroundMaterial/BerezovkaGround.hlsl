// Author-owned, world-space procedural PBR. World position/height in centimeters.
// No periodic UV tile. Large domain-warped patches and cell-randomized detail.
struct GroundFns {
 float hash(float2 p) { float3 q=frac(float3(p.xyx)*.1031);q+=dot(q,q.yzx+33.33);return frac((q.x+q.y)*q.z); }
 float noise(float2 p) {float2 i=floor(p),f=frac(p);f=f*f*(3-2*f);return lerp(lerp(hash(i),hash(i+float2(1,0)),f.x),lerp(hash(i+float2(0,1)),hash(i+1),f.x),f.y);}
 float fbm(float2 p) {float v=0,a=.57;[unroll]for(int i=0;i<4;i++){v+=a*noise(p);p=mul(float2x2(.8,-.6,.6,.8),p)*2.13+17.13;a*=.47;}return v;}
 float segment(float2 p,float2 a,float2 b) {float2 v=b-a;return length(p-a-v*saturate(dot(p-a,v)/dot(v,v)));}
 float roadDist(float2 p) {float d=1e9; /* ROAD_SEGMENTS */ return d;}
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
return max(color*Tint,0.002);
