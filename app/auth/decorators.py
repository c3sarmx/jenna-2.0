from functools import wraps

from flask import jsonify, session

from app.services.business_users import user_has_business_access


def require_business_access(view):
    @wraps(view)
    def wrapped_view(business_id, *args, **kwargs):
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({
                "error": "authentication required"
            }), 401

        if not user_has_business_access(user_id, business_id):
            return jsonify({
                "error": "business access denied"
            }), 403

        return view(business_id, *args, **kwargs)

    return wrapped_view
