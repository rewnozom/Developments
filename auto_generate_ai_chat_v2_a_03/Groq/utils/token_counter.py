import tiktoken

def count_tokens_in_string(string: str, encoding_name: str = "cl100k_base") -> int:
    """Return the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    return len(encoding.encode(string))

def count_tokens_in_messages(messages, encoding_name: str = "cl100k_base") -> int:
    """Return the number of tokens used by a list of messages."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = 0
    tokens_per_message = 3
    tokens_per_name = 1

    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with assistant
    return num_tokens
