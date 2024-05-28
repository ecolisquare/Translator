import json

SUCCESS = 0
ERROR = -1
with open('config.json', 'r') as f:
    try:
        config = json.load(f)['statusCode']
        SUCCESS = config.get('success', 200)
        ERROR = config.get('error', 400)
    except FileNotFoundError:
        print("config.json not found")
    except KeyError:
        print("statusCode not found in config.json")


