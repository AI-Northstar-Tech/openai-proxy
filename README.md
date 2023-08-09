# **OpenAI Proxy Server**

A backend **proxy server** for setting quota per user, usage monitoring and tracking of OpenAI requests.

## **Features**

- **Token Usage Pricing** utilizing the official pricing from OpenAI for different types of requests such as **Chat Completion** and **Embeddings**.
- Tracking each request and response for each particular user by giving each user a separate API key, connected to the same OpenAI key.

## **Requirements**

- Any **Relational Database** supported by SQLAlchemy (we use SQLite by default)
- **OpenAI API Key**

## **Installation (Administrator)**

- The default database is SQLite. Unless specified, a proxy_api.db file is created.
- Any SQL Database, that is supported by SQLAlchemy, can be chosen. A database must be created.
- Clone the repository and install the requirements.

```sh
pip install -r requirements.txt
```

- You need to have an authentication **username** and **password**, which will only be used to make calls to the proxy server to create **new API keys**.
- You can either setup the environment variables while running the [setup-proxy-server.py](./setup-proxy-server.py) file or set them in the .env file according to the [sample.env](./sample.env) file.

```sh
python ./setup-proxy-server.py --help
usage: setup-proxy-server.py [-h] [-o {SQLite,}]
                             [-t {postgresql,mysql,mssql}]
                             [-m {psycopg2,mysql-connector-python,pyodbc}]
                             [-u DB_USERNAME] [-w DB_PASSWORD]
                             [-b DB_HOST] [-d DB_NAME]
                             [-a OPENAI_API_KEY]
                             [-n PROXY_SERVER_USER]
                             [-p PROXY_SERVER_PASS]

OpenAI API Proxy Server

options:
  -h, --help            show this help message and exit
  -o {SQLite,}, --db_option {SQLite,}
                        Set to Others to use a non SQLite
                        Database, defaults to SQLite
  -t {postgresql,mysql,mssql}, --db_type {postgresql,mysql,mssql}
                        Database Type, for eg.: postgresql
  -m {psycopg2,mysql-connector-python,pyodbc}, --db_module {psycopg2,mysql-connector-python,pyodbc}
                        Database Module, for eg.: psycopg2
  -u DB_USERNAME, --db_username DB_USERNAME
                        Database Username
  -w DB_PASSWORD, --db_password DB_PASSWORD
                        Database Password
  -b DB_HOST, --db_host DB_HOST
                        Database URL, defaults to localhost
  -d DB_NAME, --db_name DB_NAME
                        Database Name
  -a OPENAI_API_KEY, --openai_api_key OPENAI_API_KEY
                        OpenAI API Key
  -n PROXY_SERVER_USER, --proxy_server_user PROXY_SERVER_USER
                        Admin Username for the Proxy Server
  -p PROXY_SERVER_PASS, --proxy_server_pass PROXY_SERVER_PASS
                        Admin Password for the Proxy Server
```
- Run the Flask Application

```sh
waitress-serve --port=5000  wsgi:app
```

## **User Instructions**

- Create an API key to make calls to the proxy server. This can be run only once for a given username, so the API key must be saved immediately.

- Administrator can generate the API key using [create_api_key](./create_api_key.py).
```sh
python create_api_key.py --help
usage: create_api_key.py [-h] [-u USERNAME] [-a ADMIN] [-p PASSWORD] [-q QUOTA]

Create an API key for a user.

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        The username for which to create an API key.
  -a ADMIN, --admin ADMIN
                        The admin username to create an API key.
  -p PASSWORD, --password PASSWORD
                        The admin password to create an API key.
  -q QUOTA, --quota QUOTA
                        The quota (in USD) to assign to the API key.
```

- To use the API key, run the following lines of code before making API calls to OpenAI

```python
import openai
openai.api_key = '**********************************************'
openai.api_base = f'{SERVER_URL}/{PROXY_API_KEY}/v1'
```

- The **openai.api_key** must contain the `***` value as above to make it work.
- Requests can then be made normally to OpenAI Chat Completion and Embedding Models

```python
chat_completion = ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Tell me in detail about AINorthstar Tech"}],
)
```
