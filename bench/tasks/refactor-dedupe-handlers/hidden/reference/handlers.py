USERS = {"u1": {"name": "Alice", "active": True}, "u2": {"name": "Bob", "active": False}}


def _validated_user(user_id):
    # shared-validation-block
    if not isinstance(user_id, str) or not user_id:
        return None, {"error": "invalid id", "status": 400}
    user = USERS.get(user_id)
    if user is None:
        return None, {"error": "not found", "status": 404}
    if not user["active"]:
        return None, {"error": "inactive", "status": 403}
    return user, None


def _handler(user_id, render):
    user, err = _validated_user(user_id)
    if err:
        return err
    return {"status": 200, "data": render(user)}


def get_profile(user_id):
    return _handler(user_id, lambda u: {"name": u["name"]})


def get_greeting(user_id):
    return _handler(user_id, lambda u: f"Hello, {u['name']}!")


def get_name_length(user_id):
    return _handler(user_id, lambda u: len(u["name"]))
