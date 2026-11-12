import urllib.request,json,sys,os
URL=os.environ.get("FINALCOIL_MCP_URL","http://127.0.0.1:8000/mcp")
def request(body,session=None):
    headers={"Content-Type":"application/json","Accept":"application/json, text/event-stream"}
    if session:headers["Mcp-Session-Id"]=session
    with urllib.request.urlopen(urllib.request.Request(URL,data=json.dumps(body).encode(),headers=headers),timeout=600) as r:
        return json.load(r),r.headers.get("Mcp-Session-Id")
_,sid=request({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"FinalCoilTerrain","version":"1"}}})
params=json.load(open(sys.argv[2],encoding="utf-8-sig")) if len(sys.argv)>2 else {}
r,_=request({"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":sys.argv[1],"arguments":params}},sid)
if len(sys.argv)>3:
    json.dump(r,open(sys.argv[3],"w",encoding="utf-8"),ensure_ascii=False,indent=2)
print(json.dumps({"saved":sys.argv[3],"isError":r.get("result",{}).get("isError",False)}) if len(sys.argv)>3 else json.dumps(r,ensure_ascii=True))


