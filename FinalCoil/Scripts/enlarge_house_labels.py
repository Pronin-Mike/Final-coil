import unreal,os,json
R='D:/GameDevelop/FinalCoil';E=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);LV=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert LV.save_current_level()
by={a.get_actor_label():a for a in E.get_all_level_actors()};rows=[]
for ident in ['H%02d'%i for i in range(1,13)]+['E%02d'%i for i in range(1,8)]+['G01']:
 a=by.get(ident+'_Label')
 if not a:
  a=E.spawn_actor_from_class(unreal.TextRenderActor,unreal.Vector());a.set_actor_label(ident+'_Label');a.set_folder_path('53_PlotOutlines_10Are/HouseLabels')
 house=by.get(ident+'_LogHouse') or by[ident+'_House'];p=house.get_actor_location()
 a.set_actor_location(unreal.Vector(p.x,p.y,p.z+2200),False,False)
 a.set_actor_rotation(unreal.Rotator(pitch=90,yaw=180,roll=0),False);a.set_actor_scale3d(unreal.Vector(1,1,1));a.set_is_temporarily_hidden_in_editor(False)
 a.set_actor_hidden_in_game(False)
 c=a.text_render;c.set_visibility(True,True);c.set_hidden_in_game(False)
 c.set_text(ident)
 c.set_world_size(1600);c.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
 c.set_text_render_color(unreal.Color(255,245,190,255));c.set_editor_property('cast_shadow',False)
 rows.append(dict(id=ident,world_size_cm=1600,text=str(c.get_editor_property('text'))))
assert LV.save_current_level()
os.makedirs(R+'/Review/HouseLabels',exist_ok=True)
json.dump(dict(saved=True,labels=rows),open(R+'/Review/HouseLabels/result.json','w',encoding='utf-8'),ensure_ascii=False,indent=2)
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(6500,6000,65000),unreal.Rotator(pitch=-90,yaw=0,roll=0))
unreal.log('HOUSE_LABELS_LARGE_OK count=20')
