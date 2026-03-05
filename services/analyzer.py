from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from mongo_client import get_collection

# ── TF-IDF vectorizer — fitted once, reused across all requests ───────────────

_vectorizer: TfidfVectorizer = None


def _get_vectorizer(corpus: list[str]) -> TfidfVectorizer:
    global _vectorizer
    if _vectorizer is None:
        _vectorizer = TfidfVectorizer()
        _vectorizer.fit(corpus)
    return _vectorizer


def reset_vectorizer():
    """Call this if the roles collection is updated at runtime."""
    global _vectorizer
    _vectorizer = None


# ── MongoDB helpers ───────────────────────────────────────────────────────────

def _roles_col():
    return get_collection("roles")


def get_available_roles() -> list[str]:
    return [doc["role_id"] for doc in _roles_col().find({}, {"role_id": 1, "_id": 0})]


def _fetch_role(role_id: str) -> dict | None:
    return _roles_col().find_one({"role_id": role_id}, {"_id": 0})


# ── Core analysis ─────────────────────────────────────────────────────────────

def analyze_skill_gap(role_id: str, user_skills: list[str]) -> dict | None:
    role = _fetch_role(role_id)
    if not role:
        return None

    required     = role["required_skills"]
    nice_to_have = role.get("nice_to_have", [])
    user_set     = {s.strip().lower() for s in user_skills}

    matched_required = [s for s in required     if s.lower() in user_set]
    missing_required = [s for s in required     if s.lower() not in user_set]
    matched_bonus    = [s for s in nice_to_have if s.lower() in user_set]
    missing_bonus    = [s for s in nice_to_have if s.lower() not in user_set]

    # TF-IDF similarity — vectorizer fitted once, reused on all subsequent calls
    role_doc  = " ".join(required + nice_to_have)
    user_doc  = " ".join(user_skills)
    vec       = _get_vectorizer([role_doc])
    matrix    = vec.transform([role_doc, user_doc])
    tfidf_score = round(float(cosine_similarity(matrix[0], matrix[1])[0][0]) * 100, 1)

    total_required  = len(required)
    readiness_score = round((len(matched_required) / total_required) * 100, 1) if total_required else 0.0
    readiness_label = "Ready" if readiness_score >= 80 else "Developing" if readiness_score >= 50 else "Beginner"

    return {
        "role_id":                 role_id,
        "role_title":              role["title"],
        "readiness_score":         readiness_score,
        "readiness_label":         readiness_label,
        "tfidf_similarity_score":  tfidf_score,
        "matched_required_skills": matched_required,
        "missing_required_skills": missing_required,
        "matched_bonus_skills":    matched_bonus,
        "missing_bonus_skills":    missing_bonus,
        "summary": {
            "total_required":        total_required,
            "matched_required":      len(matched_required),
            "total_nice_to_have":    len(nice_to_have),
            "matched_nice_to_have":  len(matched_bonus),
        },
    }