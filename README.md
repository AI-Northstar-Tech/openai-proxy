# **Openai Proxy Server**

A backend **Proxy server** for quota, usage monitoring and tracking of OpenAI requests

## **Features**

- **PostgresSQL database** setup to maintain all the request and responses using **sqlalchemy** and **pyscopg2** python modules
- **Token Usage Pricing** utilizing the official pricing from openai for different types of requests such as **Chat Completion**, **Embeddings**.


## **Additional Requirements**
- Any **Relational Database** which has python support
- **Openai API Key**

## **Setup Instructions**
- First of all you need to setup a flask environment and install all the requirenemts from [requirements.txt](./requirements.txt)

- Then you need to setup a postgreSQL database and set the corresponding environment variables in [sample.env](./sample.env) file.

- As a next step, you will require a **Openai_API_Key** which will be used to create requests to openai servers, you can also set it up using the [sample.env](./sample.env) file.

- At last you need to have an authentication **username** and **password** to create **new api keys** which can only be used to create calls to the server. To set their value look at [sample.env](./sample.env) file.

    You can simply craete an api by making a request to the folllowing url <br>
        ```
        {Base_Server_Url}/create_api_key/{name_of_person}
        ```

    Also you need to pass these url params for authentication <br>
        ```
        user=****
        password=***
        ```
    
    The request will return your api key generated <br> **DON'T FORGET TO COPY IT**

# Using the Proxy API KEY

In your python code you just need to **use** the following lines of code instead of providing the openai-api-key
```
openai.api_key = 'pk-**********************************************'
openai.api_base = f'https://{Base_Server_Url}/{proxy_api_key}/v1'
```
The **openai.api_key** must contain some value so, you can provide any garbage to it doesn't matter because the requests are being transfered to the backend server.

After using this you can simply use the default **openai-functions** for you particular use case. <br>

**DAMN :)**