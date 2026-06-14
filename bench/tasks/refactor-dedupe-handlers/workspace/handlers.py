USERS = {"u1": {"name": "Alice", "active": True}, "u2": {"name": "Bob", "active": False}}


def get_profile(user_id):
    # shared-validation-block
    if not isinstance(user_id, str) or not user_id:
        return {"error": "invalid id", "status": 400}
    user = USERS.get(user_id)
    if user is None:
        return {"error": "not found", "status": 404}
    if not user["active"]:
        return {"error": "inactive", "status": 403}
    return {"status": 200, "data": {"name": user["name"]}}


def get_greeting(user_id):
    # shared-validation-block
    if not isinstance(user_id, str) or not user_id:
        return {"error": "invalid id", "status": 400}
    user = USERS.get(user_id)
    if user is None:
        return {"error": "not found", "status": 404}
    if not user["active"]:
        return {"error": "inactive", "status": 403}
    return {"status": 200, "data": f"Hello, {user['name']}!"}


def get_name_length(user_id):
    # shared-validation-block
    if not isinstance(user_id, str) or not user_id:
        return {"error": "invalid id", "status": 400}
    user = USERS.get(user_id)
    if user is None:
        return {"error": "not found", "status": 404}
    if not user["active"]:
        return {"error": "inactive", "status": 403}
    return {"status": 200, "data": len(user["name"])}
