"""Reproducible local Unreal MCP requests; no editor launch or implicit mutation."""
import json,os,urllib.request
class Client:
 def __init__(self):
  self.url=os.environ.get('FINALCOIL_MCP_URL','http://127.0.0.1:8001/mcp');self.sid=None
  self.request('initialize',dict(protocolVersion='2024-11-05',capabilities={},clientInfo=dict(name='FinalCoilMeadow',version='1')))
 def request(self,method,params):
  h={'Content-Type':'application/json','Accept':'application/json, text/event-stream'}
  if self.sid:h['Mcp-Session-Id']=self.sid
  with urllib.request.urlopen(urllib.request.Request(self.url,json.dumps(dict(jsonrpc='2.0',id=1,method=method,params=params)).encode(),h),timeout=180) as r:self.sid=r.headers.get('Mcp-Session-Id',self.sid);v=json.load(r)
  assert not v.get('error') and not v.get('result',{}).get('isError'),str(v)[:2000]
  return v['result']
 def tool(self,toolset,name,**arguments):return self.request('tools/call',dict(name='call_tool',arguments=dict(toolset_name=toolset,tool_name=name,arguments=arguments)))
if __name__=='__main__':
 import sys
 c=Client()
 if sys.argv[1]=='start':print(c.tool('EditorToolset.EditorAppToolset','StartPIE',options=dict(bSimulate=False,playMode='PlayMode_InEditorFloating',warmupSeconds=0)))
 elif sys.argv[1]=='stop':print(c.tool('EditorToolset.EditorAppToolset','StopPIE'))
