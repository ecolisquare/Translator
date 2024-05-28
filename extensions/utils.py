import tiktoken

def estimate_token_num(text: str, modelname: str) -> int:
    try:
        encoding = tiktoken.get_encoding(modelname)
    except ValueError as e:
        if modelname == "babbage-002":
            encoding = tiktoken.get_encoding("cl100k_base")
        else:
            print(e)
            print(f"Invalid model name: {modelname}")
            return 0
    return len(encoding.encode(text))

# 预估训练需要的token数目
def estimate_token_num_with_path(path: str, modelname: str) -> int:
    with open(path, 'r') as file:
        text = file.read()
    return estimate_token_num(text, modelname)