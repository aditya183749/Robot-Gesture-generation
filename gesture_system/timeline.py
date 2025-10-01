import json
import re
from typing import Dict, List, Tuple, Optional

WORD_RE = re.compile(r"[A-Za-z']+")
MAX_PHRASE_LEN = 3
MIN_GESTURE_DURATION = 0.25  # seconds

def _tokenize(text: str) -> List[str]:
    return [m.group(0) for m in WORD_RE.finditer(text.lower())]

def _greedy_phrase_match(tokens: List[str], vocab: Dict[str, str]) -> List[Tuple[str, int, int]]:
    out = []
    i = 0
    n = len(tokens)
    while i < n:
        matched = False
        for L in range(min(MAX_PHRASE_LEN, n - i), 0, -1):
            phrase = " ".join(tokens[i:i+L])
            gesture = vocab.get(phrase)
            if gesture:
                out.append((gesture, i, i+L))
                i += L
                matched = True
                break
        if not matched:
            out.append((None, i, i+1))
            i += 1
    return out

def _distribute_times(start: float, end: float, tokens: List[str]) -> List[Tuple[float, float]]:
    n = max(1, len(tokens))
    total = max(0.001, end - start)
    step = total / n
    times = [(start + i*step, start + (i+1)*step) for i in range(n)]
    return times

def build_timeline(segments: List[Dict], vocab: Dict[str, str], predictor=None) -> List[Dict]:
    events = []
    for seg in segments:
        seg_tokens = _tokenize(seg["text"])
        times = _distribute_times(seg["start"], seg["end"], seg_tokens)
        matches = _greedy_phrase_match(seg_tokens, vocab)

        per_token_gesture = [None] * len(seg_tokens)
        for gesture, i0, i1 in matches:
            if gesture is not None:
                for k in range(i0, i1):
                    per_token_gesture[k] = gesture

        unknown_idxs = [i for i, g in enumerate(per_token_gesture) if g is None]
        if predictor and unknown_idxs:
            unk_tokens = [seg_tokens[i] for i in unknown_idxs]
            preds = predictor.predict(unk_tokens)
            for idx, g in zip(unknown_idxs, preds):
                per_token_gesture[idx] = g
        else:
            for i in unknown_idxs:
                per_token_gesture[i] = "neutral"

        raw = []
        for (tok_start, tok_end), g in zip(times, per_token_gesture):
            if tok_end - tok_start < MIN_GESTURE_DURATION:
                tok_end = tok_start + MIN_GESTURE_DURATION
            raw.append({"start": float(tok_start), "end": float(tok_end), "gesture": str(g)})

        if not raw:
            continue
        merged = [raw[0]]
        for ev in raw[1:]:
            last = merged[-1]
            if ev["gesture"] == last["gesture"] and abs(ev["start"] - last["end"]) < 1e-6:
                last["end"] = ev["end"]
            else:
                merged.append(ev)

        events.extend(merged)

    for ev in events:
        if ev["end"] < ev["start"]:
            ev["end"] = ev["start"]
        ev["start"] = max(0.0, float(ev["start"]))
        ev["end"] = max(ev["start"], float(ev["end"]))
    return events

def save_plan(events: List[Dict], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"animation_plan": events}, f, indent=2)
