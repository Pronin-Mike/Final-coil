"""Owned D3D12 offscreen standalone: native 1080p, matched in-process A/B.

CSV frame commands invoke only the saved meadow actor. The map is never saved
by the game. Native Shot images prove the render target size (no HighResShot).
"""
from pathlib import Path
import argparse,json,subprocess,time,shutil,struct,csv,os,re
ROOT=Path(__file__).resolve().parents[1];Q=ROOT/'Review/MeadowVegetation'
def run(quality):
 validation=json.loads((Q/os.environ.get('FINALCOIL_BENCH_INVENTORY','editor_validation.json')).read_text());actor=validation['output_actor_name'];installation=json.loads((Q/'installation.json').read_text());assert installation['quality']==quality
 engine=Path('C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe');log=ROOT/'Saved/MeadowVegetation'/('standalone_'+quality+'.log');log.parent.mkdir(parents=True,exist_ok=True)
 frame_commands=','.join(['60:BugItGo 18000 29600 210 0 90 0',f'75:ke {actor} SetActorHiddenInGame true',f'550:ke {actor} SetActorHiddenInGame false',f'1100:ke {actor} SetActorHiddenInGame true',f'1250:Shot filename={Q.as_posix()}/{quality}_native_before.png -nosuffix','1260:LogLoc',f'1600:ke {actor} SetActorHiddenInGame false',f'1750:Shot filename={Q.as_posix()}/{quality}_native_after.png -nosuffix','1760:LogLoc'])
 args=[str(engine),str(ROOT/'FinalCoil.uproject'),'/Game/FinalCoil/Maps/L_Berezovka_Terrain','-game','-RenderOffscreen','-windowed','-ResX=1920','-ResY=1080','-ForceRes','-NoSound','-unattended','-nosplash','-csvGpuStats','-csvCaptureFrames=2100','-ExitAfterCsvProfiling','-csvCategories=Basic,Rendering,RHI,RenderThread,Gpu,Memory','-csvExecCmds='+frame_commands,'-ExecCmds=r.VSync 0,t.MaxFPS 0,t.IdleWhenNotForeground 0,r.ScreenPercentage 100,r.DynamicRes.OperationMode 0','-ABSLOG='+str(log),'-ModelContextProtocolPort=8011']
 csvdir=ROOT/'Saved/Profiling/CSV';existing=set(csvdir.glob('*.csv')) if csvdir.exists() else set();start=time.monotonic();process=subprocess.Popen(args,creationflags=subprocess.CREATE_NO_WINDOW);print('Standalone '+quality+' PID '+str(process.pid),flush=True)
 try:code=process.wait(timeout=420)
 except subprocess.TimeoutExpired:process.terminate();raise RuntimeError('Owned standalone timed out')
 assert code==0,(code,str(log));text=log.read_text(encoding='utf-8',errors='replace');match=re.search(r'Writing CSV to file : (.+\.csv)',text);assert match,'No standalone CSV produced';source=(engine.parent/match.group(1)).resolve();assert source.is_file(),source;dest=Q/'csv'/('standalone_'+quality+'.csv');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
 sizes={}
 for phase in ['before','after']:
  path=Q/(quality+'_native_'+phase+'.png');raw=path.read_bytes();assert raw[:8]==b'\x89PNG\r\n\x1a\n';sizes[phase]=list(struct.unpack('>II',raw[16:24]));assert sizes[phase]==[1920,1080],sizes
 text=log.read_text(encoding='utf-8',errors='replace');assert f"SetActorHiddenInGame true' on instance" in text and 'call succeeded' in text
 result=dict(status='passed',mode='UnrealEditor -game -RenderOffscreen D3D12',quality=quality,seconds=time.monotonic()-start,native_render_sizes=sizes,actor=actor,instances=validation['total_instances'],csv=str(dest.relative_to(ROOT)),measurement_csv_rows=dict(before=[1350,1550],after=[1800,2000]),warmup_cycle_rows=dict(before=[250,500],after=[780,1030]),command_line=args,log=str(log.relative_to(ROOT)))
 (Q/(quality+'_standalone.json')).write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--quality',required=True,choices=['Low','Medium','High']);run(p.parse_args().quality)
