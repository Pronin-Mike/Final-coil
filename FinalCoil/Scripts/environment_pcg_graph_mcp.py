"""Create/update the single PCG master via live editor MCP, binding current config."""
from pathlib import Path
import json,os,urllib.request
ROOT=Path(__file__).resolve().parents[1];URL=os.environ.get('FINALCOIL_MCP_URL','http://127.0.0.1:8001/mcp');sid=None
def request(method,params):
 global sid
 h={'Content-Type':'application/json','Accept':'application/json, text/event-stream'}
 if sid:h['Mcp-Session-Id']=sid
 with urllib.request.urlopen(urllib.request.Request(URL,json.dumps(dict(jsonrpc='2.0',id=1,method=method,params=params)).encode(),h),timeout=180) as r:sid=r.headers.get('Mcp-Session-Id',sid);result=json.load(r)
 assert not result.get('error') and not result.get('result',{}).get('isError'),str(result)[:1200]
 return result
def tool(toolset,action,**kwargs):return request('tools/call',dict(name='call_tool',arguments=dict(toolset_name=toolset,tool_name=action,arguments=kwargs)))
def value(result):return json.loads(result['result']['content'][0]['text'])['returnValue']
request('initialize',dict(protocolVersion='2024-11-05',capabilities={},clientInfo=dict(name='FinalCoilEnvironmentGraph',version='1')))
graph='/Game/FinalCoil/Environment/PCG/Core/PCG_Environment_Master'
if not value(tool('editor_toolset.toolsets.asset.AssetTools','exists',path=graph)):
 tool('PCGToolset.PCGToolset','CreateGraph',name='PCG_Environment_Master',path='/Game/FinalCoil/Environment/PCG/Core')
tool('EditorToolset.EditorAppToolset','OpenEditorForAsset',assetPath=graph)
tool('editor_toolset.toolsets.programmatic.ProgrammaticToolset','get_execution_environment')
config=json.loads((ROOT/'SourceArt/EnvironmentZones/zones.json').read_text());names=[c['id'] for c in config['test_cells'] if c['id']!='world_overview'];script=(ROOT/'Scripts/environment_pcg_graph_tools.py').read_text().replace('CELL_NAMES = None','CELL_NAMES = '+repr(names))
result=tool('editor_toolset.toolsets.programmatic.ProgrammaticToolset','execute_tool_script',script=script)
report=ROOT/'Review/EnvironmentZones';(report/'graph_authoring.json').write_text(json.dumps(result,indent=2))
structure=value(tool('PCGToolset.PCGToolset','GetGraphStructure',graph=dict(refPath=graph+'.PCG_Environment_Master')));(report/'graph_structure.json').write_text(json.dumps(structure,indent=2))
print('Environment master updated from current cell config; no duplicate graph created.')
