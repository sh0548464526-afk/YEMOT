from flask import Flask, request
import requests
import os

app = Flask(__name__)


@app.route("/", methods=["GET"])
def main_router():

    req_type = request.args.get("type", "")

    handlers = {
        "filter_Value": filter_value,
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

    # בניית Token
    if len(token) > 15:
        api_token = token
    else:
        api_token = f"{ApiDID}:{token}"

    api_url = "https://www.call2all.co.il/ym/api/GetTextFile"

    try:
        response = requests.get(
            api_url,
            params={
                "Token": api_token,
                "what": what
            },
            timeout=15
        )

        data = response.json()

    except Exception as e:
        return f"error={e}"

    contents = data.get("contents", "")

    config = {}

    for line in contents.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            config[k.strip()] = v.strip()

    result_folder = ""

    if key in config:

        if config[key] == value_a:
            result_folder = go_to_a

        elif config[key] == value_b:
            result_folder = go_to_b

    return f"go_to_folder={result_folder}"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)