"""
services/chatbot_service.py
Rule-based marketing chatbot for Version 1.0.

This is deliberately simple (keyword matching against a knowledge
base) so it can be swapped for an LLM-powered service in a future
version without changing the route contract: get_answer(question) -> str.
"""

_KNOWLEDGE_BASE = [
    {
        "keywords": ["what is ctr", "click through rate", "click-through rate"],
        "answer": (
            "CTR (Click Through Rate) measures how often people who see your ad click on it. "
            "It's calculated as clicks divided by impressions, shown as a percentage. "
            "A higher CTR usually means your ad creative and targeting are resonating with the audience."
        ),
    },
    {
        "keywords": ["what is roas", "return on ad spend"],
        "answer": (
            "ROAS (Return On Ad Spend) tells you how much revenue you earn for every dollar spent on ads. "
            "It's calculated as revenue divided by ad spend. A ROAS of 4 means $4 in revenue for every $1 spent. "
            "A ROAS below 1 means your campaigns are losing money."
        ),
    },
    {
        "keywords": ["what is cpc", "cost per click"],
        "answer": (
            "CPC (Cost Per Click) is the average amount you pay for each click on your ad, "
            "calculated as ad spend divided by clicks. Lower CPC generally means more efficient spending."
        ),
    },
    {
        "keywords": ["what is cpa", "cost per acquisition", "cost per conversion"],
        "answer": (
            "CPA (Cost Per Acquisition) is the average cost to acquire one conversion, "
            "calculated as ad spend divided by conversions. Lowering CPA while maintaining "
            "volume is a common optimization goal."
        ),
    },
    {
        "keywords": ["improve campaign", "improve campaigns", "improve performance", "optimize"],
        "answer": (
            "A few ways to improve campaign performance: test different ad creatives and headlines, "
            "refine audience targeting, pause underperforming campaigns or platforms, and reallocate "
            "budget toward campaigns with the highest ROAS."
        ),
    },
    {
        "keywords": ["generate report", "generate reports", "download report", "how do i generate"],
        "answer": (
            "To generate a report: upload a campaign CSV on the Upload Data page, let it process, "
            "then go to the Reports page and click Download. Your report will include KPIs, "
            "campaign breakdowns, and insights."
        ),
    },
    {
        "keywords": ["hello", "hi", "hey"],
        "answer": "Hi! I can answer questions about CTR, ROAS, CPC, CPA, and how to improve campaigns or generate reports.",
    },
]

_DEFAULT_ANSWER = (
    "I'm not sure about that yet. I can currently answer questions about CTR, ROAS, CPC, CPA, "
    "how to improve campaigns, and how to generate reports."
)


def get_answer(question: str) -> str:
    if not question or not question.strip():
        return "Please ask a question - for example, 'What is ROAS?'"

    normalized = question.strip().lower()

    for entry in _KNOWLEDGE_BASE:
        if any(keyword in normalized for keyword in entry["keywords"]):
            return entry["answer"]

    return _DEFAULT_ANSWER
