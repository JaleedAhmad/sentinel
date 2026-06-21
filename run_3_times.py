import subprocess
import os
import json

def run_3_times():
    env = os.environ.copy()
    env["SENTINEL_MODE"] = "dev"
    env["SENTINEL_TARGET_CONFIG"] = "nudged"

    results = []

    for i in range(3):
        print(f"\n--- RUN {i+1} ---")
        if os.path.exists("summary.json"):
            os.remove("summary.json")

        subprocess.run(["python", "main.py"], env=env)

        if os.path.exists("summary.json"):
            with open("summary.json", "r") as f:
                summary = json.load(f)
                results.append(summary)
                print(f"Run {i+1} Summary: {summary}")
        else:
            print(f"Run {i+1} failed to produce summary.json")

    print("\n\n=== FINAL RESULTS OF 3 RUNS ===")
    for i, res in enumerate(results):
        print(f"Run {i+1}: Attempts = {res.get('total_attempts')}, Skill = {list(res.get('success_rate_by_skill', {}).keys())}")

if __name__ == "__main__":
    run_3_times()
