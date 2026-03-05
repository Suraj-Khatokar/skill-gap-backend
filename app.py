from flask import Flask, jsonify, request
from services import analyze_skill_gap, get_available_roles
from flask_cors import CORS
app = Flask(__name__)
CORS(app)


# ── Health check ─────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return jsonify({"status": "ok"})


# ── Roles ─────────────────────────────────────────────────────────────────────

@app.get("/roles")
def list_roles():
    return jsonify({"roles": get_available_roles()})


# ── Analyze ───────────────────────────────────────────────────────────────────

@app.post("/analyze")
def analyze():
    body = request.get_json(silent=True)

    if not body:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    role_id = body.get("role_id", "").strip().lower().replace(" ", "_")
    user_skills = body.get("skills", [])

    if not role_id:
        return jsonify({"error": "'role_id' is required."}), 400

    if not isinstance(user_skills, list) or not user_skills:
        return jsonify({"error": "'skills' must be a non-empty list."}), 400

    result = analyze_skill_gap(role_id, user_skills)

    if result is None:
        available = get_available_roles()
        return jsonify({
            "error": f"Role '{role_id}' not found.",
            "available_roles": available,
        }), 404

    return jsonify(result), 200


# ── Error handlers ────────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found."}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed."}), 405


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error."}), 500


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    
    app.run(debug=True, port=5000)
