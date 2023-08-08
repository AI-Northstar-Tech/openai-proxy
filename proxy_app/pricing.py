from proxy_app.utils import (
    get_engine_max_tokens,
    get_price_per_token,
    token_counter,
    get_message_padding,
    MAX_TOKEN_LIMIT,
)


class HandlePricing:
    def __init__(self, req_data, type):
        self.type = type
        self.req_data = req_data
        self.stream = False
        self.prompt_cost = 0

    def parse_args(self):
        messages = self.req_data["messages"] if "messages" in self.req_data else ""
        model = self.req_data["model"] if "model" in self.req_data else "gpt-3.5-turbo"
        max_tokens = (
            self.req_data["max_tokens"]
            if "max_tokens" in self.req_data
            else MAX_TOKEN_LIMIT
        )
        n = self.req_data["n"] if "n" in self.req_data else 1
        total_tokens = (
            self.req_data["total_tokens"] if "total_tokens" in self.req_data else None
        )

        return {
            "messages": messages,
            "model": model,
            "max_tokens": max_tokens,
            "n": n,
            "total_tokens": total_tokens,
        }

    def stream_pricing_estimate(self, stream_resp_tokens):
        if self.stream:
            parsed_args = self.parse_args()
            stream_completion_cost = 0
            stream_completion_cost += stream_resp_tokens * get_price_per_token(
                parsed_args["model"] + "-completion"
            )

            return round(
                self.prompt_cost + (parsed_args["n"] * stream_completion_cost), 10
            )
        else:
            return 0

    def get_pricing_estimate(self):
        if self.type == "chat_completions":
            prompt_cost = 0
            completion_cost = 0

            # Pre-request estimation with max_tokens
            prompt_tokens = 0
            parsed_args = self.parse_args()
            for message in parsed_args["messages"]:
                token_len = (
                    token_counter(message["content"], parsed_args["model"])
                    + token_counter(message["role"], parsed_args["model"])
                    + get_message_padding(parsed_args["model"])
                )
                prompt_tokens += token_len
                prompt_cost += token_len * get_price_per_token(
                    parsed_args["model"] + "-prompt"
                )

            self.prompt_cost = prompt_cost

            try:
                is_stream = self.req_data["stream"]
                if is_stream:
                    self.stream = True
            except KeyError:
                pass

            completion_cost += (
                get_engine_max_tokens(parsed_args["model"]) - prompt_tokens
            ) * get_price_per_token(parsed_args["model"] + "-completion")

            return round(self.prompt_cost + (parsed_args["n"] * completion_cost), 10)

        elif self.type == "embeddings":
            model = "text-embedding-ada-002"
            cost = 0

            if type(self.req_data["input"]) == str:
                self.req_data["input"] = [self.req_data["input"]]

            for phrase in self.req_data["input"]:
                token_len = token_counter(phrase, model)
                cost += token_len * get_price_per_token(model)
            return round(cost, 10)
