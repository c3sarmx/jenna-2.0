from flask import Blueprint, jsonify

from app.database.connection import get_connection


health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "dukkah-2.0"
    })


@health_bp.get("/health/db")
def health_db():
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            result = cur.fetchone()

        return jsonify({
            "status": "ok",
            "database": "connected",
            "result": result[0]
        })

    finally:
        conn.close()
