from datetime import datetime
from pymongo import MongoClient
from config import MONGO_URI, PKT

_client = None
_collection = None
_below_threshold_collection = None


def _get_collection():
    global _client, _collection
    if _collection is None:
        _client = MongoClient(MONGO_URI)
        _collection = _client["office_monitor"]["project_evaluations"]
    return _collection


def _get_below_threshold_collection():
    global _client, _below_threshold_collection
    if _below_threshold_collection is None:
        _client = MongoClient(MONGO_URI) if _client is None else _client
        _below_threshold_collection = _client["office_monitor"]["low_relevancy_evaluations"]
    return _below_threshold_collection


def log_evaluation(title, platform, evaluations):
    """
    Save a project + all consultant scores to MongoDB.

    Document shape:
    {
        "title":         "Interim CFO / Finance Transformation",
        "platform":      "BTG",
        "evaluated_at":  <datetime PKT>,
        "evaluations": [
            {
                "consultant":   "Richu",
                "score":        85,
                "match_reasons": [...],
                "top_pars":     [...]
            },
            ...
        ],
        "matched_count": 2   # consultants >= MIN_SCORE
    }
    """
    from config import MIN_SCORE

    high_relevancy = [e for e in evaluations if e.get("score", 0) >= MIN_SCORE]
    low_relevancy = [e for e in evaluations if e.get("score", 0) < MIN_SCORE]

    doc = {
        "title":         title,
        "platform":      platform,
        "evaluated_at":  datetime.now(PKT),
        "evaluations":   evaluations,
        "matched_count": len(high_relevancy),
        "below_threshold_count": len(low_relevancy),
        "matched_consultants": [e.get("consultant") for e in high_relevancy],
        "below_threshold_consultants": [e.get("consultant") for e in low_relevancy],
        "below_threshold_evaluations": low_relevancy,
    }

    try:
        col = _get_collection()
        result = col.insert_one(doc)
        print(f"  💾 Saved to DB — id: {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        print(f"  ⚠️  DB save failed: {e}")
        return None


def log_below_threshold(title, platform, below_threshold_evaluations):
    """
    Save only consultants with < MIN_SCORE to dedicated low-relevancy collection.

    Document shape:
    {
        "title":       "Interim CFO / Finance Transformation",
        "platform":    "BTG",
        "evaluated_at": <datetime PKT>,
        "consultants": [
            {
                "consultant":       "Jack",
                "score":            45,
                "match_reasons":    [...],
                "top_pars":         [...]
            },
            ...
        ]
    }
    """
    if not below_threshold_evaluations:
        return None  # no low-relevancy consultants, skip

    doc = {
        "title":       title,
        "platform":    platform,
        "evaluated_at": datetime.now(PKT),
        "consultants": below_threshold_evaluations,
        "count":       len(below_threshold_evaluations),
    }

    try:
        col = _get_below_threshold_collection()
        result = col.insert_one(doc)
        print(f"  📊 Saved {len(below_threshold_evaluations)} low-relevancy consultant(s) to DB")
        return str(result.inserted_id)
    except Exception as e:
        print(f"  ⚠️  Low-relevancy DB save failed: {e}")
        return None
