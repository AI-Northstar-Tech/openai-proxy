DEFAULT_INITIAL_QUOTA = 20
MAX_TOKEN_LIMIT = 1000
import tiktoken

price_per_token = {
    "text-ada-001": 0.0004 / 1000,
    "text-babbage-001": 0.0005 / 1000,
    "text-curie-001": 0.002 / 1000,
    "text-davinci-003": 0.02 / 1000,
    "ada-finetuned": 0.0016 / 1000,
    "babbage-finetuned": 0.0024 / 1000,
    "curie-finetuned": 0.0120 / 1000,
    "davinci-finetuned": 0.1200 / 1000,
    "ada-finetuned-training": 0.0004 / 1000,
    "babbage-finetuned-training": 0.0006 / 1000,
    "curie-finetuned-training": 0.0030 / 1000,
    "davinci-finetuned-training": 0.0300 / 1000,
    "text-embedding-ada-002": 0.0004 / 1000,
    "1024x1024": 0.02,
    "512x512": 0.018,
    "256x256": 0.016,
    "gpt-3.5-turbo-prompt": 0.002 / 1000,
    "gpt-3.5-turbo-completion": 0.002 / 1000,
    "gpt-4-prompt": 0.03 / 1000,  # default 8k model
    "gpt-4-completion": 0.06 / 1000,  # default 8k model
}

engine_max_tokens = {
    "text-ada-001": 2048,
    "text-babbage-001": 2048,
    "text-curie-001": 2048,
    "text-davinci-003": 4000,
    "ada-finetuned": 2048,
    "babbage-finetuned": 2048,
    "curie-finetuned": 2048,
    "davinci-finetuned": 4000,
    "ada-finetuned-training": 2048,
    "babbage-finetuned-training": 2048,
    "curie-finetuned-training": 2048,
    "davinci-finetuned-training": 4000,
    "text-embedding-ada-002": 2048,
    "gpt-3.5-turbo": 4096,
    "gpt-4": 8192,
}


def get_price_per_token(engine):
    if engine in price_per_token:
        return price_per_token[engine]
    else:
        if "ada" in engine:
            return price_per_token["ada-finetuned"]
        elif "babbage" in engine:
            return price_per_token["babbage-finetuned"]
        elif "curie" in engine:
            return price_per_token["curie-finetuned"]
        elif "davinci" in engine:
            return price_per_token["davinci-finetuned"]
        else:
            return 0.1200 / 1000


def get_engine_max_tokens(engine):
    if engine in engine_max_tokens:
        return engine_max_tokens[engine]
    else:
        if "ada" in engine:
            return engine_max_tokens["ada-finetuned"]
        elif "babbage" in engine:
            return engine_max_tokens["babbage-finetuned"]
        elif "curie" in engine:
            return engine_max_tokens["curie-finetuned"]
        elif "davinci" in engine:
            return engine_max_tokens["davinci-finetuned"]
        else:
            return 2048


def token_counter(prompt, model):
    encoder = (
        tiktoken.encoding_for_model(model)
        if model
        else tiktoken.get_encoding("cl100k_base")
    )
    token_len = len(encoder.encode(prompt))

    return token_len


def get_message_padding(model):
    message_padding = 0
    if not model:
        pass
    elif model == "gpt-4":
        message_padding = 3
    elif model == "gpt-3.5-turbo":
        message_padding = 4
    return message_padding


def price_calculator_embedding_completion(usage):
    model = "text-embedding-ada-002"
    return round(usage["total_tokens"] * get_price_per_token(model), 10)


def price_calculator_chat_completion(usage, model="gpt-3.5-turbo"):
    return round(
        usage["prompt_tokens"] * get_price_per_token(model + "-prompt")
        + usage["completion_tokens"] * get_price_per_token(model + "-completion"),
        10,
    )
