import json,sys,os
B=sys.argv[1]; import os.path as _p; m=json.load(open(f"{B}/ab-mapping.json" if _p.exists(f"{B}/ab-mapping.json") else f"{B}/mapping-private.json")); g=json.load(open(f"{B}/gold.json"))
S={"new":dict(wins=0,score=0,level=0,count=0,caught=0,planted=0,real=0,nit=0,fix=0),"legacy":None}
S["legacy"]=dict(S["new"]); ties=0; rows=[]
for cid,ab in m.items():
    p=f"{B}/verdicts/{cid}.json"
    if not os.path.exists(p): rows.append((cid,"MISSING")); continue
    v=json.load(open(p)); w=v.get("winner")
    if w=="tie": ties+=1
    for lab in("A","B"):
        s=S[ab[lab]]; r=v[lab]
        if w==lab: s["wins"]+=1
        s["score"]+=r["score"]; s["fix"]+=r["fix_quality"]
        s["level"]+=bool(r["level_ok"]); s["count"]+=bool(r["count_ok"])
        s["caught"]+=len(r["gold_caught"]); s["planted"]+=len(g[cid]["gold"])
        s["real"]+=sum(e["ruling"]=="real" for e in r["extras"]); s["nit"]+=sum(e["ruling"]!="real" for e in r["extras"])
    win={"A":ab["A"],"B":ab["B"]}.get(w,"tie")
    rows.append((cid,g[cid]["level"],win,f"new {v[[k for k in ab if ab[k]=='new'][0]]['score']} / legacy {v[[k for k in ab if ab[k]=='legacy'][0]]['score']}"))
for r in rows: print(*r)
print("ties",ties)
for k,s in S.items(): print(k,s)
