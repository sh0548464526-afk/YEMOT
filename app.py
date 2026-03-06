from flask import Flask, request
import requests
import os

app = Flask(__name__)


@app.route("/", methods=["GET"])
def main_router():
    req_type = request.args.get("type", "")

    handlers = {
        "filter_Value": filter_value,
        # ניתן להוסיף פונקציות נוספות כאן בעתיד
    }

    if req_type in handlers:
        return handlers[req_type]()

    return "unknown_type"


def filter_value():
    ApiDID  = request.args.get("ApiDID", "")
    token   = request.args.get("token", "")
    what    = request.args.get("what", "")
    key     = request.args.get("key", "")
    value_a = request.args.get("value_a", "")
    value_b = request.args.get("value_b", "")
    go_to_a = request.args.get("go_to_a", "")
    go_to_b = request.args.get("go_to_b", "")

    # בניית Token לפי אורך
    api_token = token if len(token) > 15 else f"{ApiDID}:{token}"

    api_url = "https://www.call2all.co.il/ym/api/GetTextFile"

    try:
        response = requests.get(
            api_url,
            params={"Token": api_token, "what": what},
            timeout=15
        )
        data = response.json()
    except Exception as e:
        return f"go_to_folder="  # במקרה של שגיאה, מחזיר ריק

    # וודא שה-API החזיר OK
    if data.get("responseStatus") != "OK":
        return "go_to_folder="

    contents = data.get("contents", "")

    # בניית מילון key=value
    config = {}
    for line in contents.splitlines():
        line = line.strip()
        if not line or "=" not in line:
            continue
        k, v = line.split("=", 1)
        config[k.strip()] = v.strip()  # הסרת רווחים סביב המפתח והערך

    key_value = config.get(key, "").strip()  # הערך בפועל אחרי ניקוי רווחים

    # קביעה לפי value_a/value_b
    if key_value == value_a:
        return f"go_to_folder={go_to_a}"
    elif key_value == value_b:
        return f"go_to_folder={go_to_b}"
    else:
        return "go_to_folder="  # אם הערך לא תואם


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))

    app.run(host="0.0.0.0", port=port)

print("CONFIG RECEIVED:", repr(config))
print("KEY VALUE:", repr(key_value))
print("VALUE_A:", repr(value_a), "VALUE_B:", repr(value_b))
