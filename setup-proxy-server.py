#!/usr/bin/env python3

import argparse
import os
import getpass

parser = argparse.ArgumentParser(description="OpenAI API Proxy Server")
parser.add_argument(
    "-o",
    "--db_option",
    type=str,
    default="SQLite",
    help="Set to Others to use a non SQLite Database, defaults to SQLite",
    choices=["SQLite", ""],
    action="store",
)
parser.add_argument(
    "-t",
    "--db_type",
    type=str,
    help="Database Type, for eg.: postgresql",
    choices=["postgresql", "mysql", "mssql"],
)
parser.add_argument(
    "-m",
    "--db_module",
    type=str,
    help="Database Module, for eg.: psycopg2",
    choices=["psycopg2", "mysql-connector-python", "pyodbc"],
)
parser.add_argument("-u", "--db_username", type=str, help="Database Username")
parser.add_argument("-w", "--db_password", type=str, help="Database Password")
parser.add_argument(
    "-b",
    "--db_host",
    type=str,
    default="localhost",
    help="Database URL, defaults to localhost",
)
parser.add_argument(
    "-d", "--db_name", type=str, help="Database Name", default="proxy_server"
)
parser.add_argument(
    "-a",
    "--openai_api_key",
    type=str,
    help="OpenAI API Key (skip if already set in env)",
)
parser.add_argument(
    "-n", "--proxy_server_user", type=str, help="Admin Username for the Proxy Server"
)
parser.add_argument(
    "-p", "--proxy_server_pass", type=str, help="Admin Password for the Proxy Server"
)

args, unknown = parser.parse_known_args()

if args.db_type != None:
    os.environ["DB_TYPE"] = args.db_type
if args.db_module != None:
    os.environ["DB_MODULE"] = args.db_module
if args.db_username != None:
    os.environ["DB_USERNAME"] = args.db_username
if args.db_password != None:
    os.environ["DB_PASSWORD"] = args.db_password
if args.db_host != None:
    os.environ["DB_HOST"] = args.db_host
if args.db_name != None:
    os.environ["DB_NAME"] = args.db_name
# if OPENAI_API_KEY is not in env, ask for it
if os.environ.get("OPENAI_API_KEY") is None:
    if args.openai_api_key is None:
        args.openai_api_key = getpass.getpass(
            prompt="Enter OpenAI API Key: ", stream=None
        )
os.environ["OPENAI_API_KEY"] = args.openai_api_key
if args.proxy_server_user is None:
    args.proxy_server_user = input("Enter Admin Username: ")
os.environ["PROXY_SERVER_USER"] = args.proxy_server_user
if args.proxy_server_pass is None:
    args.proxy_server_pass = getpass.getpass(
        prompt="Enter Admin Password: ", stream=None
    )
os.environ["PROXY_SERVER_PASS"] = args.proxy_server_pass

os.environ["DB_OPTION"] = args.db_option
# write the args to .env file
with open(".env", "w") as f:
    for key, value in vars(args).items():
        if value is not None:
            f.write(f"{key.upper()}={value}\n")
