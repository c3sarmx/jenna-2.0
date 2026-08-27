from flask import Blueprint, jsonify, request, session

from app.services.auth import authenticate_user
from app.services.users import get_user_by_id


auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/auth/login")
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "error": "email and password are required"
        }), 400

    user = authenticate_user(email, password)

    if not user:
        return jsonify({
            "error": "invalid credentials"
        }), 401

    session["user_id"] = user["id"]

    return jsonify({
        "id": user["id"],
        "email": user["email"],
        "active": user["active"],
    }), 200


@auth_bp.get("/auth/me")
def me():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "error": "authentication required"
        }), 401

    user = get_user_by_id(user_id)

    if not user:
        session.clear()

        return jsonify({
            "error": "user not found"
        }), 401

    if not user[2]:
        session.clear()

        return jsonify({
            "error": "user inactive"
        }), 403

    return jsonify({
        "id": user[0],
        "email": user[1],
        "active": user[2],
    }), 200


@auth_bp.post("/auth/logout")
def logout():
    session.clear()

    return jsonify({
        "message": "logout successful"
    }), 200
