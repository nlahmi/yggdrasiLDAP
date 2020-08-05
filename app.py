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


# @app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
# @app.route('/<path:path>', methods=['GET', 'POST'])
@app.errorhandler(404)
def not_found(e):
    print(request.host_url)
    pprint(f"Request: {request.get_json()}")
    # out = post(f"https://auth.mojang.com/{path}", json=request.get_json()).content
    # out = post(f"https://auth.mojang.com/{path}", json=request.get_json()).content
    # pprint(f"Response: {out}")
    return "", 404


@app.route("/authenticate", methods=["POST"])
def authenticate():
    inp = request.get_json()
    # pprint(inp)

    try:
        ld.simple_bind_s(inp["username"], inp["password"])
    except ldap.INVALID_CREDENTIALS:
        print("Wrong Password")
        return "", 403
    except ldap.SERVER_DOWN:
        print("LDAP seems down")
        return "", 500

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
    #        }h
    return jsonify(out), 200


@app.route("/validate", methods=["POST"])
def validate():
    # TODO: Actually check it
    pprint(request.get_json())
    return "", 204


#  Server Side  #

@app.route("/session/minecraft/join", methods=["POST"])
def join():
    # TODO: Actually check it
    pprint(request.get_json())
    inp = request.get_json()

    out = {"id": dash_profile(inp["selectedProfile"]),
           "name": "test",
           "properties": [{
               "name": "textures",
               "value": "eyJ0aW1lc3RhbXAiOjE1NzE2NjM0MjI4MDgsInByb2ZpbGVJZCI6IjE5MjUyMWI0ZWZkYjQyNWM4OTMxZjAyYTg0OTZlMTFiIiwicHJvZmlsZU5hbWUiOiJTZXJpYWxpemFibGUiLCJzaWduYXR1cmVSZXF1aXJlZCI6dHJ1ZSwidGV4dHVyZXMiOnsiU0tJTiI6eyJ1cmwiOiJodHRwOi8vdGV4dHVyZXMubWluZWNyYWZ0Lm5ldC90ZXh0dXJlL2I5MDY5NmViYzc0Y2U3YTkwMGVjOGFiZWVjMGRjMWNjYjM1MzRjMWI4YmE2Y2JkOWU4M2M1Y2Q3ZjM4MWZiNDgifX19",
               "signature": "AUhoVZnr4K3A7ZB4UcPXywL6G4nUG42esn7WKFwqeUBUcFKL6Fms1DMMkleHsjXYq9dSAgsmWeXyv6Er0JuYoYVBmOySBMaXlOyCCplTJPNSn5Z201Tur35Acv0bomUAP0XRmDQvbfn3bndsDnyaKNsYtJvjAxKcJ7V99iRViKi1VB76x4fchQNbSPvFi4ScoqqRVt0sszksmqOWDanu4WdXtdWytxt95bIhj04Rf3wOJ1wD1WQRVmeqHKM2eFB+iGPMqslFjNQStAKzhcDYah1A7hKuqMR1IhA6HsT47hGR+lqA3JMy8z9K5p58NbmElq821/oVGTbXP46tCAu3h+G/HCzG0SgTAFnIsHZaWcKZ80acUsIoQgbqrL371BVm5s1QBhqriHXEs+tRIk4bap6q1WaYoPB7wbqG4p3qwzY3kIL+f6bv1Oiwq/3nwz8NQYidFAIXGeQNOenaBOS9GUD+VXTnLodaLx4YWG3XzTCZSaOLGn7L5DRlOS6kCscke2qDqi+xNFP7JOae+VVAQyI6hT5S/2IeEkN+R13p9fHod9gClfvv/wmT7wwK5Yuk5zsboLlVGuUmPDGBrQjcSmWrT6nufDLFO2rO+Qhghozet+R4vrbdiOOSgdunZzDO8FqwsiR7Ai/LCmfaQpMEbx7z2K3vuCpbM6Lph12mEOk="
           }]}

    return jsonify(out), 200


@app.route("/session/minecraft/hasJoined", methods=["GET"])
def has_joined():
    # TODO: Actually check it
    # request.args.get("selectedProfile")
    out = {"id": dash_profile("acd74330df424bee904c6e1a02785177"),
           "name": request.args.get("username"),
           "properties": [{
               "name": "textures",
               "value": "eyJ0aW1lc3RhbXAiOjE1NzE2NjM0MjI4MDgsInByb2ZpbGVJZCI6IjE5MjUyMWI0ZWZkYjQyNWM4OTMxZjAyYTg0OTZlMTFiIiwicHJvZmlsZU5hbWUiOiJTZXJpYWxpemFibGUiLCJzaWduYXR1cmVSZXF1aXJlZCI6dHJ1ZSwidGV4dHVyZXMiOnsiU0tJTiI6eyJ1cmwiOiJodHRwOi8vdGV4dHVyZXMubWluZWNyYWZ0Lm5ldC90ZXh0dXJlL2I5MDY5NmViYzc0Y2U3YTkwMGVjOGFiZWVjMGRjMWNjYjM1MzRjMWI4YmE2Y2JkOWU4M2M1Y2Q3ZjM4MWZiNDgifX19",
               "signature": "AUhoVZnr4K3A7ZB4UcPXywL6G4nUG42esn7WKFwqeUBUcFKL6Fms1DMMkleHsjXYq9dSAgsmWeXyv6Er0JuYoYVBmOySBMaXlOyCCplTJPNSn5Z201Tur35Acv0bomUAP0XRmDQvbfn3bndsDnyaKNsYtJvjAxKcJ7V99iRViKi1VB76x4fchQNbSPvFi4ScoqqRVt0sszksmqOWDanu4WdXtdWytxt95bIhj04Rf3wOJ1wD1WQRVmeqHKM2eFB+iGPMqslFjNQStAKzhcDYah1A7hKuqMR1IhA6HsT47hGR+lqA3JMy8z9K5p58NbmElq821/oVGTbXP46tCAu3h+G/HCzG0SgTAFnIsHZaWcKZ80acUsIoQgbqrL371BVm5s1QBhqriHXEs+tRIk4bap6q1WaYoPB7wbqG4p3qwzY3kIL+f6bv1Oiwq/3nwz8NQYidFAIXGeQNOenaBOS9GUD+VXTnLodaLx4YWG3XzTCZSaOLGn7L5DRlOS6kCscke2qDqi+xNFP7JOae+VVAQyI6hT5S/2IeEkN+R13p9fHod9gClfvv/wmT7wwK5Yuk5zsboLlVGuUmPDGBrQjcSmWrT6nufDLFO2rO+Qhghozet+R4vrbdiOOSgdunZzDO8FqwsiR7Ai/LCmfaQpMEbx7z2K3vuCpbM6Lph12mEOk="
           }]}
    return jsonify(out), 200


# Utils #
def dash_profile(profile):
    return f"{profile[:8]}-{profile[8:12]}-{profile[12:16]}-{profile[16:20]}-{profile[20:]}"


if __name__ == "__main__":
    ld.set_option(ldap.OPT_REFERRALS, 0)
    app.run("127.0.0.1", port=80, debug=True)
