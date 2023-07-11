import openai

# Some random key has to be given to call openai API
openai.api_key = 'pk-**********************************************'
openai.api_base = '<BASE_SERVER_URL>'
# for eg: http://localhost:5000/<API_KEY>/v1

# Chat Completion with no streaming
# ==========================
# response = openai.ChatCompletion.create(
#   model="gpt-3.5-turbo-0613",
#   messages=[
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": "What are SVMs, tell me about this in detail?"},
        
#     ],
#     temperature=0,
# )

# print(response["choices"][0]['message']['content'])
# ==========================

# Chat Completion with Streaming
# ==========================
# response = openai.ChatCompletion.create(
#   model="gpt-3.5-turbo-0613",
#   messages=[
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": "What are SVMs, tell me about this in detail?"},
        
#     ],
#     temperature=0,
# )
# for i in response:
#     try:
#         print(i["choices"][0]['delta']['content'])
#     except KeyError:
#         pass
# ==========================


# Embeddings Generation for prompts
# ==========================
# emb = openai.Embedding.create(
#     input = "Tell me about SVM's, since they are very powerful and useful, how can I use them with embeddings.Tell me about SVM's, since they are very powerful and useful, how can I use them with embeddings.Tell me about SVM's, since they are very powerful and useful, how can I use them with embeddings.Tell me about SVM's, since they are very powerful and useful, how can I use them with embeddings.Tell me about SVM's, since they are very powerful and useful, how can I use them with embeddings.Tell me about SVM's, since they are very powerful and useful, how can I use them with embeddings.Tell me about SVM's, since they are very powerful and useful, how can I use them with embeddings.Tell me about SVM's, since they are very powerful and useful, how can I use them with embeddings.Tell me about SVM's, since they are very powerful and useful, how can I use them with embeddings.Tell me about SVM's, since they are very powerful and useful, how can I use them with embeddings.",
#     model="text-embedding-ada-002",
#     max_tokens=500,
# )

# print(emb)
# ==========================