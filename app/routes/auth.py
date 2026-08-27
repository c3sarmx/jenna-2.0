from flask import Blueprint, jsonify, request

from app.services.auth import authenticate_user


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

    return jsonify({
        "id": user["id"],
        "email": user["email"],
        "active": user["active"],
    }), 200
