import json
chunks = json.load(open('storage/chunks/doc_11c024ccf162.json', encoding='utf-8'))
for c in chunks:
    cid = c.get("chunk_id","")
    s = c.get("section","")[:50]
    t = c.get("text","")[:90].replace("\n"," ")
    print(f"{cid} | {s} | {t}")
