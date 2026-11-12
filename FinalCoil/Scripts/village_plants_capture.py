import json,os,sys,urllib.request,base64,math
ROOT="D:/GameDevelop/FinalCoil"
sys.path.insert(0,ROOT+"/Scripts")
import terrain_profile as T
phase=sys.argv[1]
poses=[("street",[1200,7000],80,-8),("stop",[-1500,-1000],60,-5),("verge",[2400,27000],5,-24)]
plan=json.load(open(ROOT+"/SourceArt/VillagePlants/planting.json"));pt=plan["plants"][4][0];poses.append(("shrubs",[pt[0]-450,pt[1]-300],math.degrees(math.atan2(300,450)),-7))
URL=os.environ.get("FINALCOIL_MCP_URL","http://127.0.0.1:8001/mcp")
def req(body,sid=None):
    h={"Content-Type":"application/json","Accept":"application/json, text/event-stream"}
    if sid:h["Mcp-Session-Id"]=sid
    with urllib.request.urlopen(urllib.request.Request(URL,data=json.dumps(body).encode(),headers=h),timeout=180) as r:return json.load(r),r.headers.get("Mcp-Session-Id")
_,sid=req({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"TerrainCompare","version":"2"}}})
records=[]
for i,(name,xy,yaw,pitch) in enumerate(poses):
    z=T.height(*xy)+165
    if name=='overview':z=36000
    args={"toolset_name":"EditorToolset.EditorAppToolset","tool_name":"CaptureViewport","arguments":{"captureTransform":{"location":{"x":xy[0],"y":xy[1],"z":z},"rotation":{"pitch":pitch,"yaw":yaw,"roll":0},"scale":{"x":1,"y":1,"z":1}},"annotations":None,"bShowUI":False}}
    r,_=req({"jsonrpc":"2.0","id":i+2,"method":"tools/call","params":{"name":"call_tool","arguments":args}},sid)
    assert not r.get("result",{}).get("isError"),str(r)[:500]
    v=json.loads(r["result"]["content"][0]["text"])["returnValue"]
    open(ROOT+"/Review/VillagePlants/"+phase+"/"+name+".png","wb").write(base64.b64decode(v["image"]["data"]))
    records.append({"name":name,"xy":xy,"ground_cm":z-165,"eye_height_cm":165,"camera":v["cameraLocation"],"rotation":v["cameraRotation"],"fov":v["cameraFOV"]})
json.dump(records,open(ROOT+"/Review/VillagePlants/"+phase+"/camera_poses.json","w"),indent=2)
print("CAPTURED",phase,len(records))
