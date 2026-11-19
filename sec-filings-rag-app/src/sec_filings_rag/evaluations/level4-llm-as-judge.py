import json
import os
from pathlib import Path
from typing import Literal

import requests
from dotenv import load_dotenv
from langfuse import Langfuse, get_client, observe, propagate_attributes
from openai import OpenAI
from pydantic import BaseModel, Field

APP_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = APP_ROOT.parents[2]
MAIN_MODEL_NAME = "google/gemma-4-31b-it:free"
JUDGE_MODEL_NAME = "baidu/ernie-5.5-flash-preview:free"

load_dotenv(WORKSPACE_ROOT / ".env")

langfuse = Langfuse()

client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1"),
)


class PromptResponseEvaluation(BaseModel):
    score: float = Field(ge=0, le=1, description="Quality score from 0 to 1")
    reasoning: str = Field(description="Explanation of the score")
    pass_fail: Literal["pass", "fail"] = Field(
        description="binary pass or fail decision"
    )


FUNDAMENTAL_EVAL_PROMPT = """You are an expert financial analyst evaluating the quality of a fundamental analysis.

INPUT (User Query):
{input}

OUTPUT (Analysis Generated):
Investment Grade: {investment_grade}
Confidence Score: {confidence_score}
Key Strengths: {key_strengths}
Key Concerns: {key_concerns}
Recommendation: {recommendation}

Evaluate this fundamental analysis based on:
1. Does the investment grade seem reasonable?
2. Are the key strengths actually strengths for this company?
3. Are the key concerns relevant and important?
4. Is the recommendation logical given the analysis?
5. Does the confidence score make sense?

Provide:
- score: 0.0 to 1.0 (1.0 = excellent analysis, 0.0 = poor analysis)
- reasoning: Brief explanation of your evaluation
- pass_fail: "pass" if score >= 0.7, otherwise "fail"
"""


def evaluate_fundamental_analysis(trace_data: dict) -> PromptResponseEvaluation:
    input_query = trace_data.get("input", {})
    output_data = trace_data.get("output", {})
    fundamental_analysis = output_data.get("fundamental_analysis", {})

    prompt = FUNDAMENTAL_EVAL_PROMPT.format(
        input=input_query.get("query", {}),
        investment_grade=fundamental_analysis.get("investment_grade", {}),
        confidence_score=fundamental_analysis.get("confidence_score", {}),
        key_strengths=", ".join(fundamental_analysis.get("key_strengths", {})),
        key_concerns=", ".join(fundamental_analysis.get("key_concerns", {})),
        recommendation=fundamental_analysis.get("recommendation", {}),
    )

    response = client.chat.completions.parse(
        model=MAIN_MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format=PromptResponseEvaluation,
    )

    return response.choices[0].message.parsed


RECOMMENDATION_EVAL_PROMPT = """You are an expert financial analyst evaluating investment recommendations.

    RECOMMENDATION:
    Action: {action}
    Confidence: {confidence}
    Rationale: {rationale}
    Key Risks: {key_risks}
    Key Opportunities: {key_opportunities}

    Evaluate this recommendation based on:
    1. Is the action (BUY/HOLD/SELL) clear and decisive?
    2. Does the confidence level match the strength of rationale?
    3. Does the rationale provide concrete reasoning?
    4. Are key risks and opportunities relevant and specific?

    Provide:
    - score: 0.0 to 1.0 (1.0 = excellent recommendation, 0.0 = poor recommendation)
    - reasoning: Brief explanation of your evaluation
    - pass_fail: "pass" if score >= 0.7, otherwise "fail"
    """


def evaluate_recommendation_quality(trace_data: dict) -> PromptResponseEvaluation:
    output_data = trace_data.get("output", {})
    final_recommendation = output_data.get("final_recommendation", {})

    action = final_recommendation.get("action", "")
    confidence = final_recommendation.get("confidence", "")
    rationale = final_recommendation.get("rationale", "")
    key_risks = ", ".join(final_recommendation.get("key_risks", []))
    key_opportunities = ", ".join(final_recommendation.get("key_opportunities", []))

    prompt = RECOMMENDATION_EVAL_PROMPT.format(
        action=action,
        confidence=confidence,
        rationale=rationale,
        key_risks=key_risks,
        key_opportunities=key_opportunities,
    )

    response = client.chat.completions.parse(
        model=JUDGE_MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format=PromptResponseEvaluation,
    )

    return response.choices[0].message.parsed


def run_llm_as_judge_evaluations():
    traces = langfuse.api.trace.list(tags=["evaluation", "integration_test"], limit=1)

    for trace in traces.data:
        trace_data = langfuse.api.trace.get(trace.id)

        if not trace_data.output:
            continue

        fundamental_eval = evaluate_fundamental_analysis(
            {"input": trace_data.input, "output": trace_data.output}
        )

        langfuse.create_score(
            trace_id=trace.id,
            name="fundamental_quality",
            value=fundamental_eval.score,
            comment=fundamental_eval.reasoning,
            data_type="NUMERIC",
        )

        recommendation_eval = evaluate_recommendation_quality(
            {"output": trace_data.output}
        )

        langfuse.create_score(
            trace_id=trace.id,
            name="recommendation_quality",
            value=recommendation_eval.score,
            comment=recommendation_eval.reasoning,
            data_type="NUMERIC",
        )

        print(
            f"{trace.name}: fundamental={fundamental_eval.score:.2f}, recommendation={recommendation_eval.score:.2f}"
        )
    langfuse.flush()


if __name__ == "__main__":
    run_llm_as_judge_evaluations()
