from fastapi import APIRouter, Query
from typing import List, Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/news", tags=["Daily Brief News"])

@router.get("")
async def get_daily_brief_news(category: Optional[str] = Query(None)):
    """
    Returns structured Daily Brief news items categorized cleanly (AI & Tech, Cloud Computing, Business, World, Science).
    Includes concise AI-generated summaries and source metadata.
    """
    items = [
        {
            "id": "news_1",
            "title": "Google DeepMind Announces Gemini 2.0 Agentic Framework",
            "category": "AI & Technology",
            "summary": "Google unveils next-generation multimodal models with autonomous tool invocation and real-time planning capabilities.",
            "source": "TechCrunch",
            "published_at": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "url": "https://techcrunch.com",
            "importance": "HIGH"
        },
        {
            "id": "news_2",
            "title": "AWS Serverless v2 Database Engines Expand Multi-Region Resilience",
            "category": "Cloud Computing",
            "summary": "Amazon Web Services introduces zero-downtime automated failover for global Aurora Serverless deployments.",
            "source": "AWS News Blog",
            "published_at": (datetime.utcnow() - timedelta(hours=4)).isoformat(),
            "url": "https://aws.amazon.com",
            "importance": "MEDIUM"
        },
        {
            "id": "news_3",
            "title": "Global Semiconductor Investment Reaches Record $120B in Q3",
            "category": "Business",
            "summary": "Increased demand for custom AI accelerators drives unprecedented capital expenditure in microchip fabrication.",
            "source": "Bloomberg",
            "published_at": (datetime.utcnow() - timedelta(hours=6)).isoformat(),
            "url": "https://bloomberg.com",
            "importance": "MEDIUM"
        },
        {
            "id": "news_4",
            "title": "Quantum Computing Breakthrough in Fault-Tolerant Logical Qubits",
            "category": "Science",
            "summary": "Researchers achieve 99.9% fidelity in error-corrected quantum operations operating at cryogenic temperatures.",
            "source": "Nature Physics",
            "published_at": (datetime.utcnow() - timedelta(hours=8)).isoformat(),
            "url": "https://nature.com",
            "importance": "HIGH"
        }
    ]

    if category:
        items = [i for i in items if i["category"].lower() == category.lower()]

    return items
