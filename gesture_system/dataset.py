import json
from typing import List, Dict, Tuple

NORMALIZE_KEYS = {
    "token": {"token", "word", "phrase", "text"},
    "gesture": {"gesture", "label", "class", "action"},
    "weight": {"weight", "score", "prior"},
}

def _normalize_entry(entry: Dict) -> Dict:
    out = {}
    for norm_key, variants in NORMALIZE_KEYS.items():
        for k in entry.keys():
            if k.lower() in variants:
                out[norm_key] = entry[k]
                break
    if "token" not in out or "gesture" not in out:
        raise ValueError(f"Invalid dataset row (needs token & gesture): {entry}")
    out["token"] = str(out["token"]).strip()
    out["gesture"] = str(out["gesture"]).strip()
    out["weight"] = float(entry.get("weight", 1.0))
    return out

def load_dataset(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [_normalize_entry(d) for d in data]

def build_vocab(dataset: List[Dict]) -> Dict[str, str]:
    best = {}
    for row in dataset:
        token = row["token"].lower()
        weight = float(row["weight"])
        gesture = row["gesture"]
        cur = best.get(token)
        if cur is None or weight > cur[0]:
            best[token] = (weight, gesture)
    return {tok: g for tok, (_, g) in best.items()}

