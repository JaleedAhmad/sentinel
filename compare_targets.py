import subprocess
import os
import json
import time

def run_pipeline(config_name: str, early_break: bool = True, max_attempts: int = 6):
    print(f"\n{'='*60}")
    eb_str = "ON" if early_break else "OFF"
    print(f"Running pipeline with SENTINEL_TARGET_CONFIG={config_name} (EARLY_BREAK={eb_str}, MAX_ATTEMPTS={max_attempts})")
    print(f"{'='*60}\n")
    
    env = os.environ.copy()
    env["SENTINEL_MODE"] = "dev"
    env["SENTINEL_TARGET_CONFIG"] = config_name
    env["SENTINEL_EARLY_BREAK"] = "true" if early_break else "false"
    env["SENTINEL_MAX_ATTEMPTS"] = str(max_attempts)
    
    if os.path.exists("attack_log.json"):
        os.remove("attack_log.json")
    if os.path.exists("summary.json"):
        os.remove("summary.json")
        
    try:
        subprocess.run(["python", "main.py"], env=env, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n[!] Pipeline aborted mid-run (exit code {e.returncode}). Preserving completed attempts for summary.")
    
    if os.path.exists("attack_log.json"):
        with open("attack_log.json", "r") as f:
            logs = json.load(f)
    else:
        logs = []
        
    print("\n[Pacing] Sleeping 30s between runs to clear Groq TPM window...")
    time.sleep(30)
    
    return logs

def aggregate_logs(logs_list):
    total_attempts = 0
    successful_exploits = 0
    max_severity = 0
    
    skill_stats = {}
    
    for log in logs_list:
        run_succeeded = False
        for attempt in log:
            total_attempts += 1
            skill = attempt.get("skill_used", "unknown")
            succeeded = attempt.get("verdict", {}).get("exploit_succeeded", False)
            severity = attempt.get("verdict", {}).get("severity", 1)
            
            if skill not in skill_stats:
                skill_stats[skill] = {"total": 0, "successes": 0}
            
            skill_stats[skill]["total"] += 1
            
            if severity > max_severity:
                max_severity = severity
                
            if succeeded:
                run_succeeded = True
                skill_stats[skill]["successes"] += 1
                
        if run_succeeded:
            successful_exploits += 1

    success_rate_by_skill = {
        skill: f"{(stats['successes'] / stats['total']) * 100:.0f}%" 
        for skill, stats in skill_stats.items()
    }
    
    return {
        "total_attempts_across_runs": total_attempts,
        "successful_exploits": successful_exploits,
        "max_severity": max_severity,
        "success_rate_by_skill": success_rate_by_skill,
        "raw_stats": skill_stats
    }

def run_phase_a():
    new_skills = ["destructive_action_injection", "unauthorized_transaction_injection"]
    # Phase A: Isolate new skills against Naive
    print("\n--- Phase A: Isolated Skill Evaluation (Naive Config) ---")
    for skill in new_skills:
        print(f"\n[PHASE A] Testing {skill}...")
        os.environ["SENTINEL_TARGET_SKILL"] = skill
        log = run_pipeline("naive", early_break=False, max_attempts=3)
        print(f"\n[PHASE A RAW LOG FOR {skill}]")
        print(json.dumps(log, indent=2))

def run_phase_b():
    # Phase B: Aggregated Evaluation
    print("\n--- Phase B: 2-Run Aggregated Evaluation (Free Choice) ---")
    if "SENTINEL_TARGET_SKILL" in os.environ:
        del os.environ["SENTINEL_TARGET_SKILL"]
        
    naive_logs = []
    for i in range(2):
        print(f"\n[NAIVE - Run {i+1}/2]")
        naive_logs.append(run_pipeline("naive", early_break=False, max_attempts=6))
        
    nudged_logs = []
    for i in range(2):
        print(f"\n[NUDGED - Run {i+1}/2]")
        nudged_logs.append(run_pipeline("nudged", early_break=True, max_attempts=6))
        
    naive_agg = aggregate_logs(naive_logs)
    nudged_agg = aggregate_logs(nudged_logs)
    
    runs_per_config = 2
    
    comparison_results = {
        "naive": {
            "runs": runs_per_config,
            "total_attempts": naive_agg["total_attempts_across_runs"],
            "successful_exploits": naive_agg["successful_exploits"],
            "max_severity": naive_agg["max_severity"],
            "success_rate_by_skill": naive_agg["success_rate_by_skill"]
        },
        "nudged": {
            "runs": runs_per_config,
            "total_attempts": nudged_agg["total_attempts_across_runs"],
            "successful_exploits": nudged_agg["successful_exploits"],
            "max_severity": nudged_agg["max_severity"],
            "success_rate_by_skill": nudged_agg["success_rate_by_skill"]
        }
    }
    
    with open("comparison_results.json", "w") as f:
        json.dump(comparison_results, f, indent=2)
        
    print("\n" + "="*60)
    print("                      COMPARISON SUMMARY")
    print("="*60)
    
    def print_config_stats(name, agg):
        print(f"\n[{name.upper()} CONFIG]")
        print(f"Total Runs:          {runs_per_config}")
        print(f"Total Attempts:      {agg['total_attempts_across_runs']}")
        print(f"Successful Exploits: {agg['successful_exploits']}")
        print(f"Max Severity:        {agg['max_severity']}")
        print("Success Rate by Skill:")
        if not agg["success_rate_by_skill"]:
             print("  None")
        for skill, rate in agg["success_rate_by_skill"].items():
             print(f"  - {skill}: {rate}")
             
    print_config_stats("naive", naive_agg)
    print_config_stats("nudged", nudged_agg)
    print("\nResults saved to comparison_results.json")

def main():
    print("Starting Target Comparison Test...\n")
    run_phase_a()
    run_phase_b()

if __name__ == "__main__":
    main()
