"""embedcheck CLI.

  embedcheck snapshot MODEL [--revision SHA] [--dtype float32] [--trust-remote-code] -o before.json
  # ... upgrade libraries (or run in another venv) ...
  embedcheck snapshot MODEL [same flags] -o after.json
  embedcheck compare before.json after.json        # exit 0 OK/WARN, 1 REGRESSED, 2 BOTH_FAIL
"""
import argparse, json, sys

def main(argv=None):
    p = argparse.ArgumentParser(prog="embedcheck", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("snapshot", help="record a model's behavior in this environment")
    s.add_argument("model"); s.add_argument("--revision"); s.add_argument("--dtype", choices=["float32", "float16", "bfloat16"])
    s.add_argument("--trust-remote-code", action="store_true"); s.add_argument("--device", default="cpu")
    s.add_argument("--threads", type=int); s.add_argument("--repeats", type=int, default=3)
    s.add_argument("--sentences", help="text file, one sentence per line (default: 20 built-in)")
    s.add_argument("--prompt", default="", help="prefix added to every sentence, e.g. 'query: '")
    s.add_argument("-o", "--out", required=True)
    c = sub.add_parser("compare", help="compare two snapshots (numpy only)")
    c.add_argument("a"); c.add_argument("b"); c.add_argument("--min-cosine", type=float, default=0.999)
    c.add_argument("--max-slowdown", type=float, default=2.0); c.add_argument("--json", action="store_true")
    c.add_argument("--warn-is-error", action="store_true")
    args = p.parse_args(argv)
    if args.cmd == "snapshot":
        from .snapshot import take_snapshot
        sents = [l.rstrip("\n") for l in open(args.sentences, encoding="utf-8") if l.strip()] if args.sentences else None
        snap = take_snapshot(args.model, args.revision, sents, args.dtype, args.trust_remote_code, args.device, args.threads, args.repeats, args.prompt)
        json.dump(snap, open(args.out, "w"))
        print(("ok" if snap["ok"] else "FAILED: " + snap.get("error", "")[:300]) + f"  -> {args.out}")
        return 0
    from .compare import compare
    a, b = json.load(open(args.a)), json.load(open(args.b))
    status, F = compare(a, b, args.min_cosine, args.max_slowdown)
    if args.json: print(json.dumps({"status": status, "findings": F}, indent=1))
    else:
        va = f"{a.get('sentence_transformers')}/{a.get('transformers')}/{a.get('torch')}"
        vb = f"{b.get('sentence_transformers')}/{b.get('transformers')}/{b.get('torch')}"
        print(f"{a.get('model')}  [{va}] -> [{vb}]: {status}")
        for f in F: print(f"  {f['level']:4s} {f['code']}: {f['msg']}")
    return {"OK": 0, "FIXED": 0, "WARN": 1 if args.warn_is_error else 0, "REGRESSED": 1, "BOTH_FAIL": 2}[status]

if __name__ == "__main__":
    sys.exit(main())
