import argparse
import os
import uuid

from proxy_app.app import get_db
from proxy_app.utils import DEFAULT_INITIAL_QUOTA

create_api_key_user = os.environ.get("PROXY_SERVER_USER")
create_api_key_pass = os.environ.get("PROXY_SERVER_PASS")

def createAPIKey(args):
    db = get_db()
    db.init_db()
    try:
        if (
            create_api_key_user == args.admin
            and create_api_key_pass == args.password
        ):
            api_key = f"{args.username}_{uuid.uuid3(uuid.NAMESPACE_DNS, args.username)}"
            if db.validate_api_key(api_key=api_key):
                resp = "Username already exists. Please try again with a different username."
            else:
                db.create_api_key_with_quota(
                    api_key=api_key, rem_quota=args.quota, req_count=0
                )
                resp = f"{api_key}"

            return resp
    except KeyError:
        return "Invalid Credentials"


def main():
    parser = argparse.ArgumentParser(description="Create an API key for a user.")
    parser.add_argument(
        "-u", "--username", help="The username for which to create an API key."
    )
    parser.add_argument(
        "-a",
        "--admin",
        help="The admin username to create an API key."
    )
    parser.add_argument(
        "-p",
        "--password",
        help="The admin password to create an API key."
    )
    parser.add_argument(
        "-q",
        "--quota",
        help="The quota (in USD) to assign to the API key.",
        default=DEFAULT_INITIAL_QUOTA,
    )

    args = parser.parse_args()
    if args.username is None:
        args.username = input("Enter a username: ")
    if args.admin is None:
        args.admin = input("Enter the admin username: ")
    if args.password is None:
        args.password = input("Enter the admin password: ")
    response = createAPIKey(args)
    print(response)


if __name__ == "__main__":
    main()
