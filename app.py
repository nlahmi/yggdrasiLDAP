from flask import Flask, jsonify, redirect, render_template, request, url_for
from requests import get, post
import jwt
import datetime
from pprint import pprint
import ldap

app = Flask(__name__)
SECRET = "s"
ld = ldap.initialize("ldap://192.168.85.130")


# @app.route("/authenticate", methods=['GET', 'POST'])
def proxy():
    pprint(f"Request: {request.get_json()}")
    out = post("https://auth.mojang.com/authenticate", json=request.get_json()).content
    pprint(f"Response: {out}")
    return out


# @app.route('/', defaults={'path': ''}, methods=["POST"])
# @app.route('/<path:path>', methods=["POST"])
def proxy_validate(path):
    pprint(f"Request: {request.get_json()}")
    out = post(f"https://auth.mojang.com/{path}", json=request.get_json()).content
    pprint(f"Response: {out}")
    return out


@app.route("/authenticate", methods=["POST"])
def authenticate():
    inp = request.get_json()
    # pprint(inp)

    try:
        ld.simple_bind_s(inp["username"], inp["password"])
    except ldap.INVALID_CREDENTIALS:
        print("wrong password")
        return "", 403

    user_id = "f22aa5d2e3384487909b1d523af991be"
    prof_id = "acd74330df424bee904c6e1a02785177"
    prof_na = inp["username"]  # "GenerationX6"

    prof = {"name": prof_na,
            "id": prof_id}

    jwt_payload = {"sub": user_id,
                   "yggt": "unknown",
                   "spr": prof_id,
                   "iss": "Yggdrasil-Auth",
                   "iat": datetime.datetime.utcnow(),
                   "exp": int((datetime.datetime.utcnow() + datetime.timedelta(days=30)).timestamp())}

    out = {
        "user": {
            "username": inp["username"],
            "id": user_id
        },
        "accessToken": jwt.encode(jwt_payload, SECRET, algorithm='HS256').decode("utf-8"),
        "availableProfiles": [prof],
        "selectedProfile": prof
    }
    if "clientToken" in inp:
        out["clientToken"] = inp["clientToken"]

    pprint(out)
    # out = {"accessToken": "test",
    #        "clientToken": None,
    #        "availableProfiles": [{
    #            "agent": "minecraft",
    #            "id": "Hex profile identifier",
    #            "name": "username",
    #            "userId": "another hex id",
    #            "createdAt": "epoch int",
    #            "legacyProfile": False,
    #            "suspended": False,
    #            "paid": True,
    #            "migrated": False
    #        }],
    #
    #        # Only if "agent" in json
    #        "selectedProfile": {
    #            "agent": "minecraft",
    #            "id": "Hex profile identifier",
    #            "name": "username",
    #            "userId": "another hex id",
    #            "createdAt": "epoch int",
    #            "legacyProfile": False,
    #            "suspended": False,
    #            "paid": True,
    #            "migrated": False
    #        },
    #
    #        # Only if requestUser == 'true'
    #        "user": {
    #            "id": "hex id",
    #            "email": "yada",
    #            "username": "mail for migrated accounts",
    #            "registerIp": "Last digit censored with a *",
    #            "migratedAt": 1420070400000,
    #            "registeredAt": 1325376000000,
    #            "passwordChangedAt": 1569888000000,
    #            "dateOfBirth": -2208988800000,
    #            "suspended": False,
    #            "blocked": False,
    #            "secured": True,
    #            "migrated": False,
    #            "emailVerified": True,
    #            "legacyUser": False,
    #            "verifiedByParent": False,
    #            "properties": [{
    #                "name": "preferredLanguage",
    #                "value": "en"
    #            }]
    #        }
    #        }
    return jsonify(out), 200


# @app.route("/validate", methods=["POST"])
def validate():
    pprint(request.json())
    return "", 204


if __name__ == "__main__":
    ld.set_option(ldap.OPT_REFERRALS, 0)
    app.run("127.0.0.1", port=80, debug=True)
