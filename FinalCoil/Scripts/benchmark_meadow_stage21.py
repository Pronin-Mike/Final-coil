"""Native 1080p in-process A/B/C with retained Stage 2 meshes, CSV and Shot.

Only engine reflected functions on the owned output/components are invoked.
First cycle warms each state; second cycle supplies 180 stable samples/state.
"""
from pathlib import Path
import argparse,csv,json,os,re,shutil,statistics,struct,subprocess,time,math
ROOT=Path(__file__).resolve().parents[1];Q=ROOT/'Review/MeadowVegetation/Stage2_1'
D='/Game/FinalCoil/Environment/Meadow';csv.field_size_limit(10000000)

def run(quality,variants=False):
    inventory=json.loads((Q/'benchmark_inventory.json').read_text())
    cfg=json.loads((ROOT/'SourceArt/MeadowVegetation/config.json').read_text());assert cfg['quality']==quality
    states=['A','B','C'] if not variants else (['A','Geometry','C'] if variants=='surface' else ['A','B','Material'] if variants=='material' else ['A','C','Wind20','NoWPO'] if variants=='wind' else ['A','C','NoShort','NoMedium','NoTall','NoHerbs','NoDry'])
    label=quality+('_'+variants if variants else '');commands=['60:BugItGo 18000 29600 210 0 90 0'];windows={};shots={};block=320;previous_old=False;previous_wpo=True;previous_distance=3000;visible={}
    for cycle in range(2):
        for index,state in enumerate(states):
            frame=1900+(cycle*len(states)+index)*block
            old=previous_old if state=='A' else state in ['B','Material'];ground=state not in ['A','B','Geometry']
            commands.append(f'{frame}:ke {inventory["actor"]} SetActorHiddenInGame '+str(state=='A').lower())
            commands.append(f'{frame}:ke MeadowGroundDetail SetVisibility {str(ground).lower()} true')
            for c in inventory['components']:
                path=D+('/ReferenceStage2/Meshes/' if old else '/Meshes/')+c['mesh']+'.'+c['mesh']
                if previous_old!=old:commands.append(f'{frame}:ke {c["name"]} SetStaticMesh {path}')
                excluded=state.startswith('No') and state[2:].lower() in c['mesh'].lower()
                if variants=='groups' and visible.get(c['name'],True)!=(not excluded):commands.append(f'{frame}:ke {c["name"]} SetVisibility {str(not excluded).lower()} true')
                visible[c['name']]=not excluded
                if previous_wpo!=(state!='NoWPO'):commands.append(f'{frame}:ke {c["name"]} SetEvaluateWorldPositionOffset {str(state!="NoWPO").lower()}')
                if variants=='wind' and previous_distance!=(2000 if state=='Wind20' else 3000):commands.append(f'{frame}:ke {c["name"]} SetWorldPositionOffsetDisableDistance {2000 if state=="Wind20" else 3000}')
            previous_distance=2000 if state=='Wind20' else 3000
            previous_old=old;previous_wpo=state!='NoWPO'
            if cycle:
                windows[state]=[frame+130,frame+310]
                path=Q/f'{label}_{state}_native.png';shots[state]=path
                commands.append(f'{frame+80}:Shot filename={path.as_posix()} -nosuffix')
    engine=Path('C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe')
    label=quality+('_'+variants if variants else '');log=ROOT/f'Saved/MeadowStage2_1/standalone_{label}.log'
    args=[str(engine),str(ROOT/'FinalCoil.uproject'),'/Game/FinalCoil/Maps/L_Berezovka_Terrain','-game','-windowed','-ResX=1920','-ResY=1080','-ForceRes','-NoSound','-unattended','-nosplash','-csvGpuStats',f'-csvCaptureFrames={1900+2*len(states)*block}','-ExitAfterCsvProfiling','-csvCategories=Basic,Rendering,RHI,RenderThread,Gpu,Memory','-csvExecCmds='+','.join(commands),'-ExecCmds=r.VSync 0,t.MaxFPS 0,t.IdleWhenNotForeground 0,r.ScreenPercentage 100,r.DynamicRes.OperationMode 0','-ABSLOG='+str(log),'-ModelContextProtocolPort=8011']
    # Keep each plan below UE's command-line limit; variants are split by purpose.
    if sum(map(len,args))>16000:raise RuntimeError('Split variant plan to respect Windows command-line length')
    start=time.monotonic();process=subprocess.Popen(args,creationflags=subprocess.CREATE_NO_WINDOW);print(f'{label} PID {process.pid}',flush=True)
    telemetry=[]
    deadline=time.monotonic()+900
    while process.poll() is None:
        if time.monotonic()>deadline:process.terminate();raise RuntimeError('Owned benchmark timeout')
        sample=subprocess.run(['nvidia-smi','--query-gpu=timestamp,pstate,clocks.gr,clocks.mem,utilization.gpu,power.draw,temperature.gpu','--format=csv,noheader'],capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
        telemetry.append(sample.stdout.strip())
        try:process.wait(timeout=10)
        except subprocess.TimeoutExpired:pass
    code=process.returncode
    (Q/f'gpu_telemetry_{label}.csv').write_text('timestamp,pstate,graphics_mhz,memory_mhz,gpu_percent,power_w,temperature_c\n'+'\n'.join(telemetry))
    assert code==0,(code,str(log))
    text=log.read_text(encoding='utf-8',errors='replace')
    assert 'call failed' not in text and 'Failed to find an object named' not in text
    assert 'SetVisibility' in text
    if not variants or variants=='material':assert 'SetStaticMesh' in text
    match=re.search(r'Writing CSV to file : (.+\.csv)',text);assert match
    source=(engine.parent/match.group(1)).resolve();dest=Q/'csv'/f'{label}.csv';dest.parent.mkdir(exist_ok=True);shutil.copy2(source,dest)
    sizes={state:list(struct.unpack('>II',p.read_bytes()[16:24])) for state,p in shots.items()};assert all(s==[1920,1080] for s in sizes.values())
    rows=list(csv.DictReader(open(dest,encoding='utf-8-sig')));phases={}
    for state,(a,b) in windows.items():
        samples=rows[a:b];assert len(samples)==b-a
        def vals(key):return [float(r.get(key) or 0) for r in samples]
        def avg(key):return statistics.mean(vals(key))
        frame=avg('FrameTime')
        phases[state]=dict(frames=b-a,fps=1000/frame,frame_ms=frame,p95_ms=sorted(vals('FrameTime'))[math.ceil((b-a)*.95)-1],gpu_ms=avg('GPUTime'),game_thread_ms=avg('GameThreadTime'),render_thread_wall_ms=avg('RenderThreadTime'),draw_calls=avg('RHI/DrawCalls'),gpu_memory_mb=avg('GPUMem/LocalUsedMB'),camera=[avg('View/Pos'+k) for k in 'XYZ'],forward=[avg('View/Forward'+k) for k in 'XYZ'],gpu_passes={k:avg(k) for k in samples[0] if isinstance(k,str) and k.startswith('GPU/')})
        for key in ['View/PosX','View/PosY','View/PosZ','View/ForwardX','View/ForwardY','View/ForwardZ']:assert max(vals(key))-min(vals(key))<.001,(state,key)
    pose=phases['A']['camera']+phases['A']['forward']
    assert all(max(abs(x-y) for x,y in zip(pose,p['camera']+p['forward']))<.001 for p in phases.values())
    result=dict(mode='visible native Standalone, D3D12',quality=quality,phases=phases,instances=inventory['instances'],hism_components=len(inventory['components']),resolution=[1920,1080],native_sizes=sizes,csv=str(dest.relative_to(ROOT)),measurement_rows=windows,seconds=time.monotonic()-start,command_line=args,render_thread_note='RenderThreadTime wall includes GPU waits, not busy CPU cost',memory_note='A/B/C visibility and mesh swaps keep both generations resident; VRAM is whole-run residency, not incremental grass allocation')
    (Q/f'performance_{label}.json').write_text(json.dumps(result,indent=2));print(json.dumps({s:{k:round(v,3) for k,v in p.items() if isinstance(v,float)} for s,p in phases.items()},indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--quality',required=True,choices=['Low','Medium','High']);p.add_argument('--variants',choices=['surface','material','groups','wind']);a=p.parse_args();run(a.quality,a.variants)
