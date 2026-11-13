// Stage 2.1: one material / one section, botanical parts encoded in UV.x.
float part=floor(UV.x*.5+.001);
float u=frac(UV.x*.5)*2;
float t=saturate(1-UV.y);
float dry=saturate(F.g*.7+F.r*.3);
float3 root=float3(.038,.067,.020),tip=float3(.15,.205,.066);
float speciesShift=part==7?.12:(part==8?-.12:(part==9?.04:0));
float3 green=lerp(float3(.065,.108,.039),float3(.17,.195,.077),saturate(dry*.7+speciesShift));
float3 col=lerp(root,tip,.25+.75*t);
col=lerp(col,green,.32);
col*=lerp(.91,1.06,F.r)*lerp(.96,1.04,R);
float vein=exp(-abs(u-.5)*50);
col*=.93+.07*vein;
// Intermittent senescent tips, tied primarily to the ecological patch.
float ageing=smoothstep(.79,.98,t)*smoothstep(.52,.78,dry)*.7;
col=lerp(col,float3(.25,.215,.108),ageing);
if(part==1)col=lerp(float3(.055,.079,.024),float3(.18,.205,.077),t);
if(part==2)col=lerp(float3(.105,.087,.042),float3(.28,.25,.135),t);
if(part==3)col=lerp(float3(.12,.135,.054),float3(.24,.22,.12),dry*.7+.2);
if(part==4)col=float3(.27,.135,.168)*(.9+.1*t);
if(part==5)col=float3(.48,.46,.33)*(.9+.1*t);
if(part==6)col=float3(.43,.31,.045)*(.9+.1*t);
if(part==7){float chevron=1-smoothstep(.025,.095,abs(t-(.5+.3*abs(u-.5)*2)));col=lerp(col,float3(.19,.23,.12),chevron*.45);}
if(part==0 || part>=7) col=col*1.17+float3(.004,.006,.005);
return max(col,0.003);
