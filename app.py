from flask import Flask, request
import requests
import os
import json
import time

# יצירת שרת Flask
app = Flask(__name__)

# -------------------------
# פונקציה להבאת קובץ מימות המשיח
# עם Retry (ניסיון נוסף אם יש תקלה)
# -------------------------

def get_text_file(api_token, what):

    api_url = "https://www.call2all.co.il/ym/api/GetTextFile"

    max_attempts = 3  # ניסיון ראשון + 2 רטרי

    for attempt in range(max_attempts):

        try:

            print(f"API TRY {attempt+1} / {max_attempts}")

            r = requests.get(
                api_url,
                params={
                    "token": api_token,
                    "what": what
                },
                timeout=15
            )

            data = r.json()

            return data

        except Exception as e:

            print("API ERROR:", str(e))

            # אם זה לא הניסיון האחרון → נמתין וננסה שוב
            if attempt < max_attempts - 1:

                print("WAITING BEFORE RETRY...")

                time.sleep(2)

            else:

                print("API FAILED AFTER ALL ATTEMPTS")

                return {}


# -------------------------
# ROUTER
# פונקציה שמנתבת את הבקשות
# -------------------------

@app.route("/", methods=["GET"])
def router():

    print("\n================ NEW REQUEST ================")

    # קבלת כל הפרמטרים
    params = dict(request.args)

    print("USER SENT:")
    print(json.dumps(params, ensure_ascii=False, indent=2))

    # סוג הפעולה
    req_type = request.args.get("type", "")

    # מיפוי פעולות לפונקציות
    handlers = {

        "filter_Value": filter_value

    }

    if req_type in handlers:

        result = handlers[req_type]()

        print("RETURN TO USER:", result)

        return result

    print("UNKNOWN TYPE")

    return "unknown_type"


# -------------------------
# FILTER VALUE FUNCTION
# בודקת ערך מתוך קובץ
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
    # קריאה ל-API
    # -------------------------

    data = get_text_file(api_token, what)

    print("API RESPONSE FROM YEMOT:")
    print(json.dumps(data, ensure_ascii=False, indent=2))

    if data.get("responseStatus") != "OK":

        print("API STATUS NOT OK")

        return "go_to_folder="

    # תוכן הקובץ
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

    # חיפוש הערך המבוקש
    key_value = config.get(key, "")

    print("SEARCH KEY:", key)
    print("FOUND VALUE:", key_value)

    # -------------------------
    # בדיקה לאן לעבור
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
# הפעלת השרת
# -------------------------

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(host="0.0.0.0", port=port)
