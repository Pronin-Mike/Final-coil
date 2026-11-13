import json
"""MCP ProgrammaticToolset payload. Reads the installed cell manifest; no filesystem roots."""
G={"refPath":"/Game/FinalCoil/Environment/PCG/Core/PCG_Environment_Master.PCG_Environment_Master"}
CELL_NAMES = None
def pcg(name,args):return execute_tool('PCGToolset.PCGToolset.'+name,json.dumps(args))['returnValue']
def add(kind,name,params,x,y,comment=''):
 return pcg('AddNode',dict(graph=G,nativeNodeType=kind,nodeName=name,jsonParams=json.dumps(params),nodeTitle=name,nodeComment=comment,xPositionIdx=x,yPositionIdx=y))
def edge(a,ap,b,bp):return pcg('ConnectNodePins',dict(fromNode=a,fromPinLabel=ap,toNode=b,toPinLabel=bp))
def ref(name):return dict(refPath=G['refPath']+':'+name)
def cell_names():
 assert CELL_NAMES is not None,'Submit through environment_pcg_graph_mcp.py to bind the current config.'
 return CELL_NAMES
def properties(instance,names):
 execute_tool('editor_toolset.toolsets.object.ObjectTools.list_properties',json.dumps(dict(instance=instance)))
 return json.loads(execute_tool('editor_toolset.toolsets.object.ObjectTools.get_properties',json.dumps(dict(instance=instance,properties=names)))['returnValue'])
def configure_markers(node):
 settings=properties(node,['settingsInterface'])['settingsInterface'];selector=properties(settings,['meshSelectorParameters'])['meshSelectorParameters']
 execute_tool('editor_toolset.toolsets.object.ObjectTools.list_properties',json.dumps(dict(instance=selector)))
 execute_tool('editor_toolset.toolsets.object.ObjectTools.set_properties',json.dumps(dict(instance=selector,values=json.dumps(dict(meshEntries=[dict(descriptor=dict(staticMesh=dict(refPath='/Engine/BasicShapes/Cube.Cube'),bodyInstance=dict(collisionProfileName='NoCollision'),bCastShadow=False,instanceEndCullDistance=12000),weight=1)])))))
def run():
 cells=sorted(cell_names())
 params=[dict(name='DebugMarkers',type='Boolean',description='Optional 10 cm instanced diagnostic markers, default off',containerType='None',defaultValueJson='false')]
 for name in cells:params.append(dict(name='Cell_'+name,type='SoftObjectPath',description='Precomputed surface / weighted zone / exclusion point data',containerType='None',defaultValueJson=json.dumps('/Game/FinalCoil/Environment/PCG/Masks/DA_Zones_'+name+'.DA_Zones_'+name)))
 assert pcg('SetGraphParams',dict(graph=G,params=params))
 structure=pcg('GetGraphStructure',dict(graph=G));existing={n['name'] for n in structure['nodes']}
 if 'UnifiedZonePoints' not in existing:add('Merge Points','UnifiedZonePoints',dict(bMergeMetadata=True),400,0,'Single source of precomputed surface and weighted zones.')
 if 'OptionalDebugMarkers' not in existing:add('Branch','OptionalDebugMarkers',dict(bOutputToB=False),1100,0,'Optional diagnostic instances, default off.')
 for i,name in enumerate(cells):
  loader=ref('Source_'+name) if 'Source_'+name in existing else add('Load PCG Data Asset','Source_'+name,dict(asset=dict(refPath='/Game/FinalCoil/Environment/PCG/Masks/DA_Zones_'+name+'.DA_Zones_'+name)),0,i*150)
  getter=ref('Param_'+name) if 'Param_'+name in existing else add('Get Graph Parameter','Param_'+name,dict(propertyPath='Cell_'+name,outputAttributeName='Cell_'+name),-300,i*150)
  edge(getter,'Out',loader,'Asset');edge(loader,'Out',ref('UnifiedZonePoints'),'In')
 filt=ref('ProtectGameplay') if 'ProtectGameplay' in existing else add('Filter Attribute Elements by Range','ProtectGameplay',dict(targetAttribute='Exclusion',minThreshold=dict(bInclusive=True,bUseConstantThreshold=True,attributeTypes=dict(type='Float',floatValue=0)),maxThreshold=dict(bInclusive=True,bUseConstantThreshold=True,attributeTypes=dict(type='Float',floatValue=.001))),750,0,'Exclusion > 0 is never sent to terrestrial vegetation outputs.')
 edge(ref('UnifiedZonePoints'),'Out',filt,'In');edge(filt,'InsideFilter',ref('OptionalDebugMarkers'),'In');edge(ref('OptionalDebugMarkers'),'Output A',ref('DefaultOutputNode'),'Out')
 get=ref('Param_DebugMarkers') if 'Param_DebugMarkers' in existing else add('Get Graph Parameter','Param_DebugMarkers',dict(propertyPath='DebugMarkers',outputAttributeName='DebugMarkers'),800,-200)
 edge(get,'Out',ref('OptionalDebugMarkers'),'bOutputToB')
 spawn=ref('DebugMarkerSpawner') if 'DebugMarkerSpawner' in existing else add('Static Mesh Spawner','DebugMarkerSpawner',{},1400,200,'Optional diagnostic instances only. Future plant placement is a separate stage.')
 edge(ref('OptionalDebugMarkers'),'Output B',spawn,'In');edge(spawn,'Out',ref('DefaultOutputNode'),'Out')
 configure_markers(spawn)
 execute_tool('editor_toolset.toolsets.asset.AssetTools.save_assets',json.dumps(dict(asset_paths=[G['refPath']])))
 return dict(graph=G,cells=cells,structure=pcg('GetGraphStructure',dict(graph=G)))
