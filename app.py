from flask import Flask, jsonify, redirect, render_template, request, url_for
from requests import get, post
from DBHelper import DB
from uuid import UUID, uuid4
import jwt
import datetime
from pprint import pprint
import ldap
import logging
import coloredlogs

app = Flask(__name__)
SECRET = "s"
ld = ldap.initialize("ldap://192.168.85.130")
DB_NAME = "test.db"
coloredlogs.install(level=logging.DEBUG, fmt="%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s")


# @app.route("/authenticate", methods=['GET', 'POST'])
# def proxy():
#     pprint(f"Request: {request.get_json()}")
#     out = post("https://auth.mojang.com/authenticate", json=request.get_json()).content
#     pprint(f"Response: {out}")
#     return out


# @app.route("/session/minecraft/join", methods=["POST"])
# def proxy2():
#     pprint(f"Request: {request.get_json()}")
#     out = post("https://sessionserver.mojang.com/session/minecraft/join", json=request.get_json()).content
#     pprint(f"Response: {out}")
#     return out


@app.errorhandler(404)
def not_found(e):
    logging.debug(f"URL: {request.host_url}, Request: {request.get_json()}")
    return "", 404


@app.route("/authenticate", methods=["POST"])
def authenticate():
    inp = request.get_json()

    # LDAP Authentication
    try:
        ld.simple_bind_s(inp["username"], inp["password"])
    except ldap.INVALID_CREDENTIALS:
        logging.warning("Wrong Password")
        return "", 403
    except ldap.SERVER_DOWN:
        logging.warning("LDAP seems down")
        return "", 500

    # Authorization is checked here (the user has to be registered in out DB)
    with DB(DB_NAME) as db:
        user = db.get_user_by_username(inp["username"])
        if not user:
            logging.warning("User not registered")
            return "", 403

        # Just to ignore stupid type checker
        user = dict(user)

    # Preparing variables
    user_id = UUID(user["user_id"]).hex
    prof_id = UUID(user["profile_id"]).hex
    prof = {"name": user["profile_name"][:16],  # Maximum of 16 chars
            "id": prof_id}
    token = uuid4().hex

    # Creating a token and committing it to DB
    with DB(DB_NAME) as db:
        db.new_token(prof_id, token, inp["clientToken"])

    # Preparing response
    jwt_payload = {"sub": user_id,
                   "yggt": token,  # Randomly generated access token
                   "spr": prof_id,
                   "iss": "YggdrasiLDAP-Auth",
                   "iat": datetime.datetime.utcnow(),
                   "exp": int((datetime.datetime.utcnow() + datetime.timedelta(days=30)).timestamp())}

    out = {
        "user": {
            "username": inp["username"],
            "id": user_id
        },
        "accessToken": jwt.encode(jwt_payload, SECRET, algorithm="HS256").decode("utf-8"),
        "availableProfiles": [prof],
        "selectedProfile": prof
    }
    if "clientToken" in inp:
        out["clientToken"] = inp["clientToken"]

    return jsonify(out), 200


@app.route("/validate", methods=["POST"])
def validate():
    inp = request.get_json()

    # Decode the JWT token, causing re-authentication on failure
    try:
        decoded = jwt.decode(inp["accessToken"], SECRET, algorithms=['HS256'], issuer="YggdrasiLDAP-Auth")
    except jwt.exceptions.InvalidSignatureError or \
           jwt.exceptions.ExpiredSignatureError or \
           jwt.exceptions.InvalidIssuerError as e:
        logging.warning(f"JWT decode error: {e}")
        return "", 403

    # Fetching the existing session from DB
    with DB(DB_NAME) as db:
        token = db.get_token(decoded["yggt"])

    # Validating the token
    if not token:
        logging.warning("Session doesn't exist")
        return "", 403
    if token["client_token"] != inp["clientToken"]:
        logging.warning("Client token does not match")
        return "", 403

    # Everything's fine
    return "", 204


@app.route("/session/minecraft/join", methods=["POST"])
def join():
    # TODO: Actually check it
    pprint(request.get_json())
    # inp = request.get_json()

    return "", 204

#  Server Side  #


@app.route("/session/minecraft/hasJoined", methods=["GET"])
def has_joined():
    # TODO: Actually check it
    # request.args.get("selectedProfile")
    pprint(request.args)
    out = {"id": str(UUID("7bdd425c-38af-4008-b593-1f9f377dc6da")),
           "name": request.args.get("username"),
           "properties": [{
               "name": "textures",
               "value": "ewogICJ0aW1lc3RhbXAiIDogMTU5NjU0NzYxNTYyOSwKICAicHJvZmlsZUlkIiA6ICI1OTgzZjkxY2UzY2M0MzdjYjc0ZTZlMTJmNWY0YzNlZCIsCiAgInByb2ZpbGVOYW1lIiA6ICJOaW5nYV9LaXR0eSIsCiAgInNpZ25hdHVyZVJlcXVpcmVkIiA6IHRydWUsCiAgInRleHR1cmVzIiA6IHsKICAgICJTS0lOIiA6IHsKICAgICAgInVybCIgOiAiaHR0cDovL3RleHR1cmVzLm1pbmVjcmFmdC5uZXQvdGV4dHVyZS81NDJkMjZhMzMxZGU5MDViNDU5NTVkNmIxMWVlMWNlMDBiMTBmNGYzMDk3NzVlNTM0ZGM3NDMzM2Q2YTlmMjg4IgogICAgfQogIH0KfQ==",
               "signature": "d5Bc318c5kj4+ZJNXCLARfHctVgmOOS3sBPyUBBuk75OI31Dww8tknqjsLCOaagybW580ZF4dSktm4+FXQnGojLRiiOdwzTF92H3fysbvKzZiRt3/sMRcxUNKXoIxF1nb7s3RdxJ5BUhYaxjKBOJXRcxh9f5J6OOkxZ5ECATi5MYBfg0phr5em3dkXz5C2yqWK1PKrylkC+S10aDBqZmXTsUuI8MmJYuCUXxkQkJdYbvZlA89joTuPvFc/9yjHLxsW1d756+Bpisp7jR/FR/0lUIh8yIdXbWeAvMU0O1q+q9GkVdTUKcZvLA0u03ript6XrQttR6uRN/XTRZPPU2bB6OBHw+axVpSbS0Birdd8CtC468u3jNVMTlLkBolVQZu9yhZ8JF3AMTecH0vn5OnqTppYlLSlyvTZAhHUdt6fLJb8POmsM+NE/PNqPoqe5TX5mPspjVR8b2I88FXgR/xaWRIsqpAm5QAQRzVzrUoxPlXvo8v04WT46e533lnIkjt7A8Cfaz/tqQAGDsf/unE797YQRnwt7aCmv7jiNDy28lKC52XrjQrAWXBV6ZH2vFsx7ZYTkJj7h7Mj5jwzEUl+ackAjiquqMhFWFda9Cp3XtQMPLfGKb+p42jJagYw8HjXkeJHn75CQ7/wdsAw6M9nAZgphcZZjnk81uwRp6Bpo="
           }]}
    return jsonify(out), 200


if __name__ == "__main__":
    ld.set_option(ldap.OPT_REFERRALS, 0)

    # with DB(DB_NAME) as d:
    #     d.conn.cursor().execute("DELETE FROM profiles")
    #     d.new_profile("KulNamesNotTaken", True, "test")
    app.run("127.0.0.1", port=80, debug=True)
