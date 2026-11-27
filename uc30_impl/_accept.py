import glob, json, os

for f in sorted(glob.glob("out/*.report.json")):
    r = json.load(open(f, encoding="utf-8"))
    print(f"{os.path.basename(f):40} {r['outcome']['verification']:11} "
          f"{r['outcome']['policy_action']:6} digest={r['claimed_digest']} "
          f"pass={r['counts']['pass']} ne={r['counts']['not_evaluated']}")

s = json.load(open("schema/ucr-v0.1.schema.json", encoding="utf-8"))
print("schema ok:", s["$id"], "| required:", len(s["required"]))
print("demo html bytes:", os.path.getsize("demo/verify-demo.html"))
