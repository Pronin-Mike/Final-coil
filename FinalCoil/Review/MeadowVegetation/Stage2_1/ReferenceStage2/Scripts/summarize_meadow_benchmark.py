"""Summarize raw engine CSV; reject moving/mismatched camera or wrong native size."""
from pathlib import Path
import json,csv,statistics,math
ROOT=Path(__file__).resolve().parents[1];Q=ROOT/'Review/MeadowVegetation';csv.field_size_limit(10000000)
def summarize(quality):
 info=json.loads((Q/(quality+'_standalone.json')).read_text());assert all(s==[1920,1080] for s in info['native_render_sizes'].values())
 rows=list(csv.DictReader(open(Q/'csv'/('standalone_'+quality+'.csv'),encoding='utf-8-sig')));phases={}
 for phase,(a,b) in info['measurement_csv_rows'].items():
  samples=rows[a:b];assert len(samples)==b-a
  def values(k):return [float(row.get(k) or 0) for row in samples]
  def avg(k):return statistics.mean(values(k))
  for k in ['View/PosX','View/PosY','View/PosZ','View/ForwardX','View/ForwardY','View/ForwardZ']:assert max(values(k))-min(values(k))<.001,(quality,phase,k)
  frame=avg('FrameTime');phases[phase]=dict(frames=len(samples),fps=1000/frame,frame_ms=frame,frame_p95_ms=sorted(values('FrameTime'))[int(len(samples)*.95)],gpu_ms=avg('GPUTime'),game_thread_ms=avg('GameThreadTime'),render_thread_wall_ms=avg('RenderThreadTime'),draw_calls=avg('RHI/DrawCalls'),gpu_local_used_mb=avg('GPUMem/LocalUsedMB'),camera=[avg('View/Pos'+axis) for axis in ['X','Y','Z']],forward=[avg('View/Forward'+axis) for axis in ['X','Y','Z']],gpu_passes={k:avg(k) for k in samples[0] if isinstance(k,str) and k.startswith('GPU/')})
 for phase,(a,b) in info['measurement_csv_rows'].items():
  if 'RHI/PrimitivesDrawn' in rows[0]:phases[phase]['rhi_primitives_drawn']=statistics.mean(float(row.get('RHI/PrimitivesDrawn') or 0) for row in rows[a:b])
 assert max(abs(x-y) for x,y in zip(phases['before']['camera']+phases['before']['forward'],phases['after']['camera']+phases['after']['forward']))<.001
 distribution=json.loads((ROOT/'SourceArt/MeadowVegetation'/('distribution_'+quality.lower()+'.json')).read_text());return dict(quality=quality,resolution=[1920,1080],mode=info['mode'],phases=phases,instances=info['instances'],group_instances={g:len(p) for g,p in distribution['groups'].items()},distribution_seconds=distribution['seconds'],delta_frame_ms=phases['after']['frame_ms']-phases['before']['frame_ms'],warmup_cycle_rows=info.get('warmup_cycle_rows'),render_thread_note='Engine RenderThreadTime is wall time including GPU waits, not busy CPU cost',memory_note='Both phases have meadow resources resident; visibility A/B does not isolate incremental asset VRAM')
if __name__=='__main__':
 result={q:summarize(q) for q in ['Low','Medium','High'] if (Q/(q+'_standalone.json')).exists()};(Q/'performance.json').write_text(json.dumps(result,indent=2));print(json.dumps({q:{p:{k:round(v,2) if isinstance(v,float) else v for k,v in phase.items() if k not in ['gpu_passes','camera','forward']} for p,phase in r['phases'].items()} for q,r in result.items()},indent=2))
