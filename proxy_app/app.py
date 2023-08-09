from flask import Flask, Response, request, stream_with_context
from proxy_app.request_handler import ChatCompletionHandler, EmbeddingHandler
from proxy_app.utils import DEFAULT_INITIAL_QUOTA, MAX_TOKEN_LIMIT
from proxy_app.Database.database import ProxyAPIDatabase
import json
import uuid
import openai
import dotenv
import os
import time

dotenv.load_dotenv(".env")
app = Flask(__name__)


def get_db():
    if os.environ.get("DB_OPTION") == "SQLite":
        db = ProxyAPIDatabase(
            os.environ.get("DB_OPTION"), None, None, None, None, None, None
        )
    else:
        db = ProxyAPIDatabase(
            os.environ.get("DB_OPTION"),
            os.environ.get("DB_TYPE"),
            os.environ.get("DB_MODULE"),
            os.environ.get("DB_USERNAME"),
            os.environ.get("DB_PASSWORD"),
            os.environ.get("DB_HOST"),
            os.environ.get("DB_NAME"),
        )
    return db


db = get_db()
db.init_db()
create_api_key_user = os.environ.get("PROXY_SERVER_USER")
create_api_key_pass = os.environ.get("PROXY_SERVER_PASS")


@app.route("/")
def appEntry():
    return (
        "<h2>Welcome to the OpenAI API Proxy Server</h2>",
        200,
        {"Content-Type": "text/html"},
    )


@app.route("/create_api_key/<string:username>", methods=["POST", "GET"])
def createAPIKey(username):
    try:
        if (
            request.args["user"] == create_api_key_user
            and request.args["password"] == create_api_key_pass
        ):
            api_key = f"{username}_{uuid.uuid3(uuid.NAMESPACE_DNS, username)}"
            if db.validate_api_key(api_key=api_key):
                resp = "Username already exists. Please try again with a different username."
            else:
                db.create_api_key_with_quota(
                    api_key=api_key, rem_quota=DEFAULT_INITIAL_QUOTA, req_count=0
                )
                resp = f"{api_key}"

            return resp, 200, {"Content-Type": "text/html"}

    except KeyError:
        return "Invalid Credentials", 200, {"Content-Type": "text/html"}


@app.route("/<string:proxy_key>/v1/chat/completions", methods=["POST", "GET"])
def handleChatCompetion(proxy_key):
    timeStart = time.time()
    # Checking if the API key is valid and that the Quota is sufficient for the request uisng tiktoken library
    req_data = json.loads(request.data.decode("utf-8"))
    if db.validate_api_key(proxy_key):
        is_valid, rem_quota, req_id = db.validate_api_key_request(proxy_key)
    else:
        is_valid = False
        rem_quota = None

    if is_valid:
        req = ChatCompletionHandler(req_data, request.full_path)
        is_valid_resp, response, stream = req.makeRequest()
        if is_valid_resp and not stream:
            tokens_used = req.total_tokens
            tokens_cost = req.tokens_cost

            print(
                f"Total Token Count: {tokens_used}, Actual Total Token Cost: {tokens_cost}"
            )
            db.insert_data(req_id, proxy_key, req_data, response)
            db.update_remQuota(proxy_key, rem_quota - tokens_cost)
            print(f"Remaining Quota: {rem_quota-tokens_cost}")

            response = Response(json.dumps(response), mimetype="application/json")

        elif is_valid_resp and stream:

            def generate_stream():
                stream_resp = list()
                resp_tokens = 0

                try:
                    req_data["max_tokens"] = min(
                        int(req_data["max_tokens"]), MAX_TOKEN_LIMIT
                    )
                except KeyError:
                    req_data["max_tokens"] = MAX_TOKEN_LIMIT

                for resp in openai.ChatCompletion.create(**req_data):
                    resp_tokens += 1
                    stream_resp.append(resp)
                    yield f"data: {resp}\n\n"

                yield (f"data: [DONE]\n\n")

                # sum up cost of tokens
                print(f"Total Token Cost: {tokens_cost}")
                db.insert_data(req_id, proxy_key, req_data, stream_resp)
                db.update_remQuota(proxy_key, rem_quota - tokens_cost)
                print(f"Remaining Quota: {rem_quota-tokens_cost}")

            return Response(
                stream_with_context(generate_stream()), mimetype="text/event-stream"
            )
    else:
        if rem_quota != None:
            response = Response(
                f"Insufficient Quota, Remaining Quota: {rem_quota}",
                mimetype="application/json",
            )
        else:
            response = Response(f"INVALID-API-KEY", mimetype="application/json")
    timeEnd = time.time()
    timeTaken = timeEnd - timeStart
    print(f"Time taken (total): {timeTaken}")
    return response


@app.route("/<string:proxy_key>/v1/embeddings", methods=["POST", "GET"])
def handleEmbedding(proxy_key):
    req_data = json.loads(request.data.decode("utf-8"))

    if db.validate_api_key(proxy_key):
        is_valid, rem_quota, req_id = db.validate_api_key_request(proxy_key)
    else:
        is_valid = False
        rem_quota = None

    if is_valid:
        req = EmbeddingHandler(req_data, request.full_path)
        is_valid_resp, response = req.makeRequest()
        if is_valid_resp:
            tokens_used = req.total_tokens
            tokens_cost = req.tokens_cost

            print(
                f"Actual Total Token Count: {tokens_used}, Actual Total Token Cost: {tokens_cost}"
            )
            db.insert_data(req_id, proxy_key, req_data, response)
            db.update_remQuota(proxy_key, rem_quota - tokens_cost)
            print(f"Remaining Quota: {rem_quota-tokens_cost}")

            response = Response(json.dumps(response), mimetype="application/json")
    else:
        if rem_quota != None:
            response = Response(
                f"Insufficient Quota, Remaining Quota: {rem_quota}",
                mimetype="application/json",
            )
        else:
            response = Response(f"INVALID-API-KEY", mimetype="application/json")

    return response


if __name__ == "__main__":
    app.run(port=os.environ.get("PORT"))
