import time
import json
from typing import List, Dict

class VirtualRobot:
    """
    A simple timeline executor. For real robots, replace `perform_gesture` with
    hardware integration (e.g., ROS publishers or serial writes).
    """
    def __init__(self, realtime: bool = False):
        self.realtime = realtime

    def perform_gesture(self, gesture: str, duration: float) -> None:
        print(f"[Robot] {gesture:<16} for {duration:.2f}s")

    def run(self, plan: List[Dict]) -> None:
        if not plan:
            print("[Robot] Empty plan.")
            return
        t0 = plan[0]["start"]
        anchor = time.time()
        for ev in plan:
            start, end, g = ev["start"], ev["end"], ev["gesture"]
            dur = max(0.0, end - start)
            if self.realtime:
                # Align to wall clock
                target = anchor + (start - t0)
                now = time.time()
                if target > now:
                    time.sleep(target - now)
                self.perform_gesture(g, dur)
                if dur > 0:
                    time.sleep(dur)
            else:
                self.perform_gesture(g, dur)

def load_plan(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        obj = json.load(f)
    return obj["animation_plan"]
