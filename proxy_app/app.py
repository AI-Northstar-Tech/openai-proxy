from flask import Flask, Response
from flask import request, stream_with_context
from proxy_app.request_handler import ChatCompletionHandler, EmbeddingHandler
from proxy_app.pricing import HandlePricing
from proxy_app.utils import DEFAULT_INITIAL_QUOTA, MAX_TOKEN_LIMIT
from proxy_app.Database.database import ProxyAPIDatabase
import json
import uuid
import openai
import dotenv
import os
dotenv.load_dotenv('.env')

app = Flask(__name__)

# import argparse

# parser = argparse.ArgumentParser(description='OpenAI API Proxy Server')
# parser.add_argument('-p','--port', type=int, default=5000, help='Port to run the server on, defaults to 5000')
# parser.add_argument('-o', '--db_option', type=bool, default=False, help='Set to true to use a non SQLite Database, defaults to False')
# parser.add_argument('-t','--db_type', type=str, help='Database Type, for eg.: postgresql')
# parser.add_argument('-m','--db_module', type=str, help='Database Module, for eg.: psycopg2')
# parser.add_argument('-u','--db_username', type=str, help='Database Username')
# parser.add_argument('-w','--db_password', type=str, help='Database Password')
# parser.add_argument('-b','--db_host', type=str, default='localhost',help='Database URL, defaults to localhost')
# parser.add_argument('-d','--db_name', type=str,help='Database Name')
# parser.add_argument('-a','--api_key', type=str, help='OpenAI API Key')
# parser.add_argument('-n', '--admin', type=str, help='Admin Username for the Proxy Server')
# parser.add_argument('-s', '--admin_pass', type=str, help='Admin Password for the Proxy Server')


# args, unknown = parser.parse_known_args()

# if(args.db_type != None):
#     os.environ['DB_TYPE'] = args.db_type
# if(args.db_module != None):
#     os.environ['DB_MODULE'] = args.db_module
# if(args.db_username != None):
#     os.environ['DB_USERNAME'] = args.db_username
# if(args.db_password != None):
#     os.environ['DB_PASSWORD'] = args.db_password
# if(args.db_host != None):
#     os.environ['DB_HOST'] = args.db_host
# if(args.db_name != None):
#     os.environ['DB_NAME'] = args.db_name
# if(args.api_key != None):
#     os.environ['OPENAI_API_KEY'] = args.api_key
# if(args.admin != None):
#     os.environ['PROXY_SERVER_USER'] = args.admin
# if(args.admin_pass != None):
#     os.environ['PROXY_SERVER_PASS'] = args.admin_pass


# if args.db_option==False:
#     db = ProxyAPIDatabase(args.db_option, None, None, None, None, None, None)
# else:
#     db = ProxyAPIDatabase(args.db_option, os.environ.get('DB_TYPE'), os.environ.get('DB_MODULE'), os.environ.get('DB_USERNAME'), os.environ.get('DB_PASSWORD'), os.environ.get('DB_HOST'), os.environ.get('DB_NAME'))

# db.init_db()

# create_api_key_user = os.environ.get('PROXY_SERVER_USER')
# create_api_key_pass = os.environ.get('PROXY_SERVER_PASS')

@app.route("/")
def appEntry():
    return (
        "<h2>Welcome to the OpenAI API Proxy Server</h2>",
        200,
        {"ContentType": "text/html"},
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
                resp = f"API Key created: {api_key}"

            return resp, 200, {"Content-Type": "text/html"}

    except KeyError:
        return "Invalid Credentials", 200, {"ContentType": "text/html"}


@app.route("/<string:proxy_key>/v1/chat/completions", methods=["POST", "GET"])
def handleChatCompetion(proxy_key):
    # Checking if the API key is valid and that the Quota is sufficient for the request uisng tiktoken library
    req_data = json.loads(request.data.decode("utf-8"))
    price_prediction = HandlePricing(req_data, "chat_completions")
    tiktoken_tokens_cost = price_prediction.get_pricing_estimate()

    if db.validate_api_key(proxy_key):
        is_valid, rem_quota, req_id = db.validate_api_key_request(
            proxy_key, tiktoken_tokens_cost
        )
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

                tokens_cost = price_prediction.stream_pricing_estimate(resp_tokens)
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
                f"Insufficient Quota, Remaining Quota: {rem_quota} and Request Cost: {tiktoken_tokens_cost}",
                mimetype="application/json",
            )
        else:
            response = Response(f"INVALID-API-KEY", mimetype="application/json")

    return response


@app.route("/<string:proxy_key>/v1/embeddings", methods=["POST", "GET"])
def handleEmbedding(proxy_key):
    req_data = json.loads(request.data.decode("utf-8"))
    price_prediction = HandlePricing(req_data, "embeddings")
    tiktoken_tokens_cost = price_prediction.get_pricing_estimate()

    if db.validate_api_key(proxy_key):
        is_valid, rem_quota, req_id = db.validate_api_key_request(
            proxy_key, tiktoken_tokens_cost
        )
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
                f"Insufficient Quota, Remaining Quota: {rem_quota} and Request Cost: {tiktoken_tokens_cost}",
                mimetype="application/json",
            )
        else:
            response = Response(f"INVALID-API-KEY", mimetype="application/json")

    return response

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='OpenAI API Proxy Server')
    parser.add_argument('-p','--port', type=int, default=5000, help='Port to run the server on, defaults to 5000')
    parser.add_argument('-o', '--db_option', type=bool, default=False, help='Set to true to use a non SQLite Database, defaults to False')
    parser.add_argument('-t','--db_type', type=str, help='Database Type, for eg.: postgresql')
    parser.add_argument('-m','--db_module', type=str, help='Database Module, for eg.: psycopg2')
    parser.add_argument('-u','--db_username', type=str, help='Database Username')
    parser.add_argument('-w','--db_password', type=str, help='Database Password')
    parser.add_argument('-b','--db_host', type=str, default='localhost',help='Database URL, defaults to localhost')
    parser.add_argument('-d','--db_name', type=str,help='Database Name')
    parser.add_argument('-a','--api_key', type=str, help='OpenAI API Key')
    parser.add_argument('-n', '--admin', type=str, help='Admin Username for the Proxy Server')
    parser.add_argument('-s', '--admin_pass', type=str, help='Admin Password for the Proxy Server')


    args, unknown = parser.parse_known_args()

    if(args.db_type != None):
        os.environ['DB_TYPE'] = args.db_type
    if(args.db_module != None):
        os.environ['DB_MODULE'] = args.db_module
    if(args.db_username != None):
        os.environ['DB_USERNAME'] = args.db_username
    if(args.db_password != None):
        os.environ['DB_PASSWORD'] = args.db_password
    if(args.db_host != None):
        os.environ['DB_HOST'] = args.db_host
    if(args.db_name != None):
        os.environ['DB_NAME'] = args.db_name
    if(args.api_key != None):
        os.environ['OPENAI_API_KEY'] = args.api_key
    if(args.admin != None):
        os.environ['PROXY_SERVER_USER'] = args.admin
    if(args.admin_pass != None):
        os.environ['PROXY_SERVER_PASS'] = args.admin_pass

    # app = Flask(__name__)

    if args.db_option==False:
        db = ProxyAPIDatabase(args.db_option, None, None, None, None, None, None)
    else:
        db = ProxyAPIDatabase(args.db_option, os.environ.get('DB_TYPE'), os.environ.get('DB_MODULE'), os.environ.get('DB_USERNAME'), os.environ.get('DB_PASSWORD'), os.environ.get('DB_HOST'), os.environ.get('DB_NAME'))

    db.init_db()

    create_api_key_user = os.environ.get('PROXY_SERVER_USER')
    create_api_key_pass = os.environ.get('PROXY_SERVER_PASS')
    app.run(port=args.port)
