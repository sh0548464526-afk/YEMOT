from flask import Flask, request
import requests
import os
import time
import json

app = Flask(__name__)

# -------------------------
# CACHE
# -------------------------

cache = {}
CACHE_TTL = 30  # שניות


# -------------------------
# פונקציה להבאת קובץ עם CACHE
# -------------------------

def get_text_file(api_token, what):

    cache_key = api_token + "|" + what
    now = time.time()

    if cache_key in cache:

        cached_data, timestamp = cache[cache_key]

        if now - timestamp < CACHE_TTL:
            print("CACHE HIT:", cache_key)
            return cached_data

        else:
            print("CACHE EXPIRED:", cache_key)

    print("CACHE MISS:", cache_key)

    api_url = "https://www.call2all.co.il/ym/api/GetTextFile"

    r = requests.get(
        api_url,
        params={
            "Token": api_token,
            "what": what
        },
        timeout=15
    )

    data = r.json()

    cache[cache_key] = (data, now)

    return data


# -------------------------
# ROUTER
# -------------------------

@app.route("/", methods=["GET"])
def router():

    print("\n================ NEW REQUEST ================")

    params = dict(request.args)

    print("USER SENT:")
    print(json.dumps(params, ensure_ascii=False, indent=2))

    req_type = request.args.get("type", "")

    handlers = {

        "filter_Value": filter_value,

        # כאן ניתן להוסיף פונקציות נוספות בעתיד
        # "something_else": something_else

    }

    if req_type in handlers:

        result = handlers[req_type]()

        print("RETURN TO USER:", result)

        return result

    print("UNKNOWN TYPE")

    return "unknown_type"


# -------------------------
# FILTER VALUE FUNCTION
# -------------------------

def filter_value():

    ApiDID  = request.args.get("ApiDID", "")
    token   = request.args.get("token", "")
    what    = request.args.get("what", "")
    key     = request.args.get("key", "")
    value_a = request.args.get("value_a", "")
    value_b = request.args.get("value_b", "")
    go_to_a = request.args.get("go_to_a", "")
    go_to_b = request.args.get("go_to_b", "")

    print("FUNCTION: filter_Value")

    print("ApiDID:", ApiDID)
    print("token:", token)
    print("what:", what)

    # -------------------------
    # בניית TOKEN
    # -------------------------

    if len(token) > 15:
        api_token = token
        print("TOKEN MODE: direct")
    else:
        api_token = f"{ApiDID}:{token}"
        print("TOKEN MODE: ApiDID:token")

    print("TOKEN SENT TO API:", api_token)

    # -------------------------
    # קריאת API
    # -------------------------

    try:

        data = get_text_file(api_token, what)

    except Exception as e:

        print("API ERROR:", str(e))

        return "go_to_folder="

    print("API RESPONSE FROM YEMOT:")
    print(json.dumps(data, ensure_ascii=False, indent=2))

    if data.get("responseStatus") != "OK":

        print("API STATUS NOT OK")

        return "go_to_folder="

    contents = data.get("contents", "")

    print("FILE CONTENTS:")
    print(contents)

    # -------------------------
    # המרה למילון
    # -------------------------

    config = {}

    for line in contents.splitlines():

        line = line.strip()

        if not line or "=" not in line:
            continue

        k, v = line.split("=", 1)

        config[k.strip()] = v.strip()

    print("PARSED CONFIG:")
    print(config)

    key_value = config.get(key, "")

    print("SEARCH KEY:", key)
    print("FOUND VALUE:", key_value)

    # -------------------------
    # בדיקה
    # -------------------------

    if key_value == value_a:

        print("MATCH VALUE A")

        return f"go_to_folder={go_to_a}"

    elif key_value == value_b:

        print("MATCH VALUE B")

        return f"go_to_folder={go_to_b}"

    else:

        print("NO MATCH")

        return "go_to_folder="


# -------------------------
# START SERVER
# -------------------------

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(host="0.0.0.0", port=port)