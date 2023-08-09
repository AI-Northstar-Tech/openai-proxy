import argparse
import os
import uuid

from proxy_app.app import get_db
from proxy_app.utils import DEFAULT_INITIAL_QUOTA

create_api_key_user = os.environ.get("PROXY_SERVER_USER")
create_api_key_pass = os.environ.get("PROXY_SERVER_PASS")


import argparse
import uuid

create_api_key_user = "username"
create_api_key_pass = "password"


def createAPIKey(args):
    db = get_db()
    try:
        # Example of matching credentials
        if (
            create_api_key_user == create_api_key_user
            and create_api_key_pass == create_api_key_pass
        ):
            api_key = f"{args.username}_{uuid.uuid3(uuid.NAMESPACE_DNS, args.username)}"
            if db.validate_api_key(api_key=api_key):
                resp = "Username already exists. Please try again with a different username."
            else:
                db.create_api_key_with_quota(
                    api_key=api_key, rem_quota=args.quota, req_count=0
                )
                resp = f"API Key created: {api_key}"

            return resp
    except KeyError:
        return "Invalid Credentials"


def main():
    parser = argparse.ArgumentParser(description="Create an API key for a user.")
    parser.add_argument(
        "-u", "--username", help="The username for which to create an API key."
    )
    parser.add_argument(
        "-q",
        "--quota",
        help="The quota (in USD) to assign to the API key.",
        default=DEFAULT_INITIAL_QUOTA,
    )

    args = parser.parse_args()
    if args.username is None:
        # get via input
        args.username = input("Enter a username: ")
    response = createAPIKey(args)
    print(response)


if __name__ == "__main__":
    main()
