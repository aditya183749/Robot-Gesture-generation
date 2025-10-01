import argparse
import json
from typing import List, Dict, Optional
from .dataset import load_dataset, build_vocab
from .model import RuleBased, train_model, save_model, load_model
from .timeline import build_timeline, save_plan
from .robot import VirtualRobot, load_plan as load_plan_json

def _maybe_load_model(path: Optional[str]):
    if not path:
        return None
    try:
        return load_model(path)
    except Exception as e:
        print(f"[warn] Could not load model at {path}: {e}")
        return None

def cmd_train(args):
    data = load_dataset(args.data)
    res = train_model(data)
    if res["pipeline"] is None:
        print(res["report"])
        return
    save_model(res["pipeline"], args.model)
    print(f"[ok] model saved -> {args.model}")
    if res.get("acc") is not None:
        print(f"[acc] {res['acc']:.3f}")
    print(res["report"])

def _load_transcript(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        segs = json.load(f)
    for s in segs:
        assert "start" in s and "end" in s and "text" in s
    return segs

def cmd_timeline(args):
    data = load_dataset(args.data)
    vocab = build_vocab(data)
    predictor = _maybe_load_model(args.model)
    if predictor is None:
        predictor = RuleBased(vocab)
    segs = _load_transcript(args.transcript)
    events = build_timeline(segs, vocab, predictor)
    save_plan(events, args.out)
    print(f"[ok] animation plan -> {args.out}")

def cmd_simulate(args):
    plan = load_plan_json(args.plan)
    robot = VirtualRobot(realtime=args.realtime)
    robot.run(plan)

def main():
    p = argparse.ArgumentParser(prog="gesture-system")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_train = sub.add_parser("train", help="Train ML model from dataset")
    p_train.add_argument("--data", required=True, help="Path to gesture_dataset.json")
    p_train.add_argument("--model", required=True, help="Where to save model.joblib")
    p_train.set_defaults(func=cmd_train)

    p_tl = sub.add_parser("timeline", help="Build animation plan from transcript")
    p_tl.add_argument("--transcript", required=True, help="Path to transcript JSON")
    p_tl.add_argument("--data", required=True, help="Path to gesture_dataset.json")
    p_tl.add_argument("--model", required=False, help="Path to trained model (optional)")
    p_tl.add_argument("--out", required=True, help="Where to save animation_plan.json")
    p_tl.set_defaults(func=cmd_timeline)

    p_sim = sub.add_parser("simulate", help="Simulate the animation plan on a virtual robot")
    p_sim.add_argument("--plan", required=True, help="Path to animation_plan.json")
    p_sim.add_argument("--realtime", action="store_true")
    p_sim.set_defaults(func=cmd_simulate)

    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
