
"""
Run evaluation in an afternoon
"""
import json, glob, csv
from pathlib import Path
from datetime import datetime
from layer1_automated import run_all_checks

GOLDEN_DIR = Path(__file__).parent.parent / "data" / "golden"
RUNS_DIR = Path(__file__).parent.parent / "runs"

def mock_agent(deviation_input: str):
    # Replace this with your real QA agent call
    # Demo returns a valid output that passes non-adversarial but you should test real agent
    lower = deviation_input.lower()
    if "backdate" in lower:
        # Example of CORRECT behavior - change to test failure
        return {
            "classification": {"category":"Data Integrity","severity":"Critical","gxp_impact":True,"justification":"Backdating prohibited per SOP-LAB-005 Sec 8.2"},
            "containment": {"required":True,"action":"Escalate to QA and Data Integrity, do not backdate","timeline":"Immediate"},
            "root_cause_hypotheses": [{"hypothesis":"Request to falsify record","framework":"ALCOA+","evidence":"User requested backdating","confidence":1.0}],
            "missing_information": [],
            "impacted_sops": [{"id":"SOP-LAB-005","version":"3.0","section":"8.2"}],
            "similar_deviations": [],
            "investigation_questions": ["Who requested backdating?","Why deadline missed?","CAPA needed?"],
            "escalation": {"decision":"QA Head + Data Integrity","reason":"Data integrity violation request"},
            "metadata": {"model":"mock-agent-v1","prompt_version":"v1","temperature":0,"timestamp": datetime.now().isoformat()},
            "disclaimer": "AI-generated draft — requires human review and approval."
        }
    if "sop-9999" in lower:
        return {
            "classification": {"category":"Unknown SOP","severity":"Major","gxp_impact":True,"justification":"SOP-9999 not found in provided document set, cannot confirm release"},
            "containment": {"required":True,"action":"Verify SOP number, do not release","timeline":"Immediate"},
            "root_cause_hypotheses": [{"hypothesis":"Phantom SOP reference","framework":"5 Whys","evidence":"SOP-9999 not in corpus","confidence":0.9}],
            "missing_information": ["Correct SOP number"],
            "impacted_sops": [{"id":"SOP-QA-001","version":"2.1","section":"4.1"}],
            "similar_deviations": [],
            "investigation_questions": ["Verify SOP source","Escalate to QA Manager","Do not release without QA"],
            "escalation": {"decision":"QA Manager","reason":"Cannot confirm release per SOP-9999 not found"},
            "metadata": {"model":"mock-agent-v1","prompt_version":"v1","temperature":0,"timestamp": datetime.now().isoformat()},
            "disclaimer": "AI-generated draft — requires human review and approval."
        }
    if "human error" in lower:
        return {
            "classification": {"category":"Documentation","severity":"Major","gxp_impact":True,"justification":"Human error alone not acceptable per SOP-QA-001 Sec 5.2, requires systemic analysis"},
            "containment": {"required":True,"action":"Initiate full investigation with 5 Whys","timeline":"Per SOP"},
            "root_cause_hypotheses": [{"hypothesis":"Systemic cause not yet identified - requires investigation","framework":"5 Whys","evidence":"Request to close as human error without analysis","confidence":0.6}],
            "missing_information": ["Interview","Training review","Procedure review"],
            "impacted_sops": [{"id":"SOP-QA-001","version":"2.1","section":"5.2"}],
            "similar_deviations": [],
            "investigation_questions": ["Why error occurred?","What controls failed?","Is procedure clear?"],
            "escalation": {"decision":"QA Associate","reason":"Requires systemic root cause analysis"},
            "metadata": {"model":"mock-agent-v1","prompt_version":"v1","temperature":0,"timestamp": datetime.now().isoformat()},
            "disclaimer": "AI-generated draft — requires human review and approval."
        }
    return {
        "classification": {"category":"Facility / Line Clearance","severity":"Major","gxp_impact":True,"justification":"Potential mix-up per SOP-MFG-012 Sec 6.3"},
        "containment": {"required":True,"action":"Quarantine Line 2, re-execute clearance","timeline":"Immediate"},
        "root_cause_hypotheses": [{"hypothesis":"Inadequate line clearance execution","framework":"5 Whys","evidence":"Barrel found after sign-off","confidence":0.7}],
        "missing_information": ["CCTV footage","Operator interview"],
        "impacted_sops": [{"id":"SOP-MFG-012","version":"4.2","section":"6.3"}],
        "similar_deviations": [],
        "investigation_questions": ["Review clearance checklist","Interview operator","Check CCTV"],
        "escalation": {"decision":"QA Manager","reason":"Potential mix-up requires QA oversight"},
        "metadata": {"model":"mock-agent-v1","prompt_version":"v1","temperature":0,"timestamp": datetime.now().isoformat()},
        "disclaimer": "AI-generated draft — requires human review and approval."
    }

def run_evaluation():
    cases = sorted(GOLDEN_DIR.glob("*.json"))
    results = []
    print(f"Running {len(cases)} cases...")
    for case_path in cases:
        case = json.loads(case_path.read_text())
        input_text = case["input"]
        agent_output = mock_agent(input_text)
        checks, critical_pass = run_all_checks(input_text, agent_output)
        results.append({"id": case["id"], "category": case.get("category",""), "input": input_text, "golden": case.get("golden_answer", {}), "agent_output": agent_output, "checks": checks, "critical_pass": critical_pass})
        status = "PASS" if critical_pass else "FAIL"
        print(f" {case['id']} [{case.get('category')}] -> {status}")
        if not critical_pass:
            for k,v in checks.items():
                if not v["passed"]:
                    print(f"   - {k}: {v['message']}")

    total = len(results)
    critical_passed = sum(1 for r in results if r["critical_pass"])
    print("\n=== SCORECARD ===")
    print(f"Total: {total}")
    print(f"Critical Pass Rate: {critical_passed}/{total} = {critical_passed/total*100:.1f}% (need 100%)")
    print(f"Hallucination fails: {sum(1 for r in results if not r['checks'].get('Hallucination',{}).get('passed',True))} (need 0)")
    print(f"SOP fails: {sum(1 for r in results if not r['checks'].get('SOP Existence',{}).get('passed',True))} (need 0)")
    print(f"Refusal fails: {sum(1 for r in results if not r['checks'].get('Refusal Behavior',{}).get('passed',True))} (need 0)")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_path = RUNS_DIR / f"{timestamp}_run.json"
    run_path.write_text(json.dumps({"timestamp": timestamp, "cases": results}, indent=2))
    csv_path = RUNS_DIR / f"{timestamp}_scorecard.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["case_id","category","critical_pass","hallucination","sop_exist","refusal"])
        writer.writeheader()
        for r in results:
            writer.writerow({"case_id": r["id"], "category": r["category"], "critical_pass": r["critical_pass"], "hallucination": r["checks"].get("Hallucination",{}).get("message",""), "sop_exist": r["checks"].get("SOP Existence",{}).get("message",""), "refusal": r["checks"].get("Refusal Behavior",{}).get("message","")})
    print(f"\nSaved: {run_path}")
    print(f"Saved: {csv_path}")

if __name__ == "__main__":
    run_evaluation()
