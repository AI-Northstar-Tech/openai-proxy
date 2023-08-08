import argparse
import os

parser = argparse.ArgumentParser(description="OpenAI API Proxy Server")
parser.add_argument('-o', '--db_option', type=str, default='SQLite', help='Set to Others to use a non SQLite Database, defaults to SQLite')
parser.add_argument("-t", "--db_type", type=str, help="Database Type, for eg.: postgresql")
parser.add_argument("-m", "--db_module", type=str, help="Database Module, for eg.: psycopg2")
parser.add_argument("-u", "--db_username", type=str, help="Database Username")
parser.add_argument("-w", "--db_password", type=str, help="Database Password")
parser.add_argument("-b", "--db_host", type=str, default="localhost", help="Database URL, defaults to localhost")
parser.add_argument("-d", "--db_name", type=str, help="Database Name")
parser.add_argument("-a", "--api_key", type=str, help="OpenAI API Key")
parser.add_argument("-n", "--admin", type=str, help="Admin Username for the Proxy Server")
parser.add_argument("-p", "--admin_pass", type=str, help="Admin Password for the Proxy Server")

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
if args.api_key != None:
    os.environ["OPENAI_API_KEY"] = args.api_key
if args.admin != None:
    os.environ["PROXY_SERVER_USER"] = args.admin
if args.admin_pass != None:
    os.environ["PROXY_SERVER_PASS"] = args.admin_pass

os.environ["DB_OPTION"] = args.db_option
