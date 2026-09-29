import json,re,sys,os
B=sys.argv[1]; import os.path as _p; m=json.load(open(f"{B}/ab-mapping.json" if _p.exists(f"{B}/ab-mapping.json") else f"{B}/mapping-private.json"))
def scrub(t):
    t="\n".join(l for l in t.splitlines() if not re.match(r'\s*(Sources?|Files? (opened|read))\s*:',l,re.I))
    t=re.sub(r'`?[\w./-]+\.md`?','[reference]',t)
    t=re.sub(r"\b(the )?(knowledge )?library'?s?\b",'the reference material',t,flags=re.I)
    t=re.sub(r'\breferences/','',t)
    return t.strip()+"\n"
missing=[]
for cid,ab in m.items():
    out=[]
    for lab in ("A","B"):
        p=f"{B}/{ab[lab]}/{cid}.md"
        if not os.path.exists(p): missing.append(p); continue
        out.append(f"===== REVIEW {lab} =====\n"+scrub(open(p).read()))
    open(f"{B}/judge-in/{cid}.md","w").write("\n".join(out))
print("missing:",missing or "none")
