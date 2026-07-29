
"""
Layer 3: Human Expert Review
Exports blind review sheets
"""
import json, csv, random
from pathlib import Path

GOLDEN_DIR = Path(__file__).parent.parent / "data" / "golden"
RUNS_DIR = Path(__file__).parent.parent / "runs"

def export_for_human_review(run_json_path: str, output_csv: str):
    run_data = json.loads(Path(run_json_path).read_text())
    cases = run_data.get("cases", [])
    random.shuffle(cases)
    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["case_id","input","golden","agent_output","reviewer1_score","reviewer1_notes","reviewer2_score","reviewer2_notes"])
        writer.writeheader()
        for c in cases:
            writer.writerow({
                "case_id": c["id"],
                "input": c["input"][:500],
                "golden": json.dumps(c.get("golden",{}))[:1000],
                "agent_output": json.dumps(c.get("agent_output",{}))[:2000],
                "reviewer1_score": "",
                "reviewer1_notes": "",
                "reviewer2_score": "",
                "reviewer2_notes": ""
            })
    print(f"Exported to {output_csv}")

if __name__ == "__main__":
    print("Usage: python layer3_human.py runs/<run>.json runs/human_review_sheet.csv")
