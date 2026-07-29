
"""
Layer 2: LLM-as-a-Judge
"""
import json

JUDGE_PROMPT = """
You are a senior QA investigator evaluating an AI agent deviation analysis.

Deviation Input:
{input}

Golden Answer:
{golden}

Agent Output:
{agent_output}

Score each dimension 1-5 with justification:
1 = Wrong/Dangerous, 3 = Acceptable with Edits, 5 = Expert-Level Audit-Ready

Dimensions: Factual Grounding, Regulatory & SOP Compliance, Patient Safety & Risk, Data Integrity ALCOA+, Citation Fidelity, Refusal Behavior, Root Cause Quality, Completeness

Return JSON with scores, overall, critical_failure, failure_reason
If any critical dimension is 1, critical_failure=true
"""

def judge_case(input_text, golden, agent_output, client=None):
    prompt = JUDGE_PROMPT.format(input=input_text, golden=json.dumps(golden, indent=2), agent_output=json.dumps(agent_output, indent=2))
    print("Integrate your LLM client here")
    print(prompt[:400])
    return {"note": "Implement LLM call"}

if __name__ == "__main__":
    print("Layer 2 template ready")
