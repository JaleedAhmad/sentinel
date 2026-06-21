import subprocess
import os
import json

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
        
    subprocess.run(["python", "main.py"], env=env)
    
    if os.path.exists("attack_log.json"):
        with open("attack_log.json", "r") as f:
            return json.load(f)
    return []

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
            
            if succeeded:
                run_succeeded = True
            
            if severity > max_severity:
                max_severity = severity
                
            if skill not in skill_stats:
                skill_stats[skill] = {"total": 0, "successes": 0}
            
            skill_stats[skill]["total"] += 1
            if succeeded:
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

def main():
    print("Starting Target Comparison Test...\n")
    
    # Phase A: Full Loop No Early Break
    print("\n--- Phase A: Full loop, no early-break (Naive Config) ---")
    naive_full_log = run_pipeline("naive", early_break=False, max_attempts=6)
    
    print("\n[PHASE A RAW RESULTS (Naive, No Early Break)]")
    for attempt in naive_full_log:
        skill = attempt.get("skill_used", "unknown")
        succeeded = attempt.get("verdict", {}).get("exploit_succeeded", False)
        severity = attempt.get("verdict", {}).get("severity", 1)
        print(f"Skill: {skill} | Succeeded: {succeeded} | Severity: {severity}")
        
    # Phase B: 3-Run Aggregated
    print("\n--- Phase B: 3-Run Aggregated Evaluation (Early-break ON) ---")
    naive_logs = []
    for i in range(3):
        print(f"\n[NAIVE - Run {i+1}/3]")
        naive_logs.append(run_pipeline("naive", early_break=True, max_attempts=6))
        
    nudged_logs = []
    for i in range(3):
        print(f"\n[NUDGED - Run {i+1}/3]")
        nudged_logs.append(run_pipeline("nudged", early_break=True, max_attempts=6))
        
    naive_agg = aggregate_logs(naive_logs)
    nudged_agg = aggregate_logs(nudged_logs)
    
    comparison_results = {
        "naive": {
            "runs": 3,
            "total_attempts": naive_agg["total_attempts_across_runs"],
            "successful_exploits": naive_agg["successful_exploits"],
            "max_severity": naive_agg["max_severity"],
            "success_rate_by_skill": naive_agg["success_rate_by_skill"]
        },
        "nudged": {
            "runs": 3,
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
        print(f"Total Runs:          3")
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

if __name__ == "__main__":
    main()
