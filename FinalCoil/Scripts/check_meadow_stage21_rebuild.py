"""Repeat native local PCG generation and compare all instance transforms."""
from pathlib import Path
import unreal,time,json,hashlib
ROOT=Path(unreal.Paths.project_dir()).resolve();Q=ROOT/'Review/MeadowVegetation/Stage2_1';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
output=next(a for a in E.get_all_level_actors() if a.get_actor_label()=='MEADOW_Output');pcg=next(a for a in E.get_all_level_actors() if a.get_actor_label()=='ENV_PCG_Environment').get_component_by_class(unreal.PCGComponent)
def fingerprint():
    rows=[]
    for c in output.get_components_by_class(unreal.InstancedStaticMeshComponent):
        transforms=[]
        for i in range(c.get_instance_count()):
            t=c.get_instance_transform(i,False);p=t.translation;r=t.rotation;s=t.scale3d
            transforms.append([round(v,5) for v in [p.x,p.y,p.z,r.x,r.y,r.z,r.w,s.x,s.y,s.z]])
        rows.append([c.static_mesh.get_name(),c.get_editor_property('instancing_random_seed'),sorted(transforms)])
    return dict(sha256=hashlib.sha256(json.dumps(sorted(rows),separators=(',',':')).encode()).hexdigest(),components=len(rows),instances=sum(len(r[2]) for r in rows))
before=fingerprint();start=time.perf_counter();pcg.generate(True);state={'ticks':0}
def tick(dt):
    state['ticks']+=1
    if state['ticks']<2 or pcg.get_editor_property('generation_in_progress'):return
    elapsed=time.perf_counter()-start
    try:
        after=fingerprint();assert before==after,(before,after)
        assert len(output.get_components_by_class(unreal.DecalComponent))==1
        result=dict(status='passed',before=before,after=after,local_pcg_wall_seconds=elapsed,duplicate_components=False)
        assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    except BaseException as e:result=dict(status='failed',error=str(e))
    (Q/'deterministic_rebuild.json').write_text(json.dumps(result,indent=2));unreal.unregister_slate_post_tick_callback(handle)
handle=unreal.register_slate_post_tick_callback(tick)
