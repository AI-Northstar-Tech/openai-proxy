# **OpenAI Proxy Server**

A backend **proxy server** for setting quota per user, usage monitoring and tracking of OpenAI requests.

## **Features**

- **Token Usage Pricing** utilizing the official pricing from OpenAI for different types of requests such as **Chat Completion** and **Embeddings**.
- Tracking each request and response for each particular user by giving each user a separate API key, connected to the same OpenAI key.

## **Requirements**

- Any **Relational Database** supported by SQLAlchemy
- **OpenAI API Key**

## **Installation (Administrator)**

- The default database is SQLite. Unless specified, a proxy_api.db file is created. 
- Any SQL Database, that is supported by SQLAlchemy, can be chosen. A database must be created.
- Clone the repository and install the requirements.

```sh
pip install -r requirements.txt
```

- You need to have an authentication **username** and **password**, which will only be used to make calls to the proxy server to create **new API keys**.
- You can either setup the environment variables while running the [setup.py](./setup.py) file or set them in the .env file according to the [sample.env](./sample.env) file.

```sh
python .\setup.py --help
usage: setup.py [-h] [-o DB_OPTION] [-t DB_TYPE] [-m DB_MODULE] [-u DB_USERNAME] [-w DB_PASSWORD] [-b DB_HOST] [-d DB_NAME] [-a API_KEY] [-n ADMIN] [-p ADMIN_PASS]

OpenAI API Proxy Server

optional arguments:
  -h, --help            show this help message and exit
  -o DB_OPTION, --db_option DB_OPTION
                        Set to Others to use a non SQLite Database, defaults to SQLite
  -t DB_TYPE, --db_type DB_TYPE
                        Database Type, for eg.: postgresql
  -m DB_MODULE, --db_module DB_MODULE
                        Database Module, for eg.: psycopg2
  -u DB_USERNAME, --db_username DB_USERNAME
                        Database Username
  -w DB_PASSWORD, --db_password DB_PASSWORD
                        Database Password
  -b DB_HOST, --db_host DB_HOST
                        Database URL, defaults to localhost
  -d DB_NAME, --db_name DB_NAME
                        Database Name
  -a API_KEY, --api_key API_KEY
                        OpenAI API Key
  -n ADMIN, --admin ADMIN
                        Admin Username for the Proxy Server
  -p ADMIN_PASS, --admin_pass ADMIN_PASS
                        Admin Password for the Proxy Server
```

- Run the Flask Application

```sh
waitress-serve --port=5000  wsgi:app
```

## **User Instructions**

- Create an API key to make calls to the proxy server. This can be run only once for a given username, so the API key must be saved immediately.

```python
url = f'{SERVER_URL}/create_api_key/{USERNAME}'
# For example http://localhost:5000/create_api_key/aintech_user
params = {"user":{ADMIN_USERNAME}, "password":{ADMIN_PASSWORD}}
print(requests.get(url = url, params = params).content)
```

- To use the API key, run the following lines of code before making API calls to OpenAI

```python
import openai
openai.api_key = '**********************************************'
openai.api_base = f'{SERVER_URL}/{PROXY_API_KEY}/v1'
```

- The **openai.api_key** must contain some value. You can provide any random value to it because the requests are being transfered to the backend server, so it doensn't matter.
- Requests can then be made normally to OpenAI Chat Completion and Embedding Models

```python
chat_completion = ChatCompletion.create(model="gpt-3.5-turbo", 
                                        messages=[{"role": "user", 
                                                   "content": "Tell me in detail about AINorthstar Tech"}])
```
