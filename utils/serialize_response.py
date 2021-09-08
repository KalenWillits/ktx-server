import json
import inspect

def serialize_response(response):
    clean_response = dict()
    for key, value in response.items():
        if inspect.isclass(key):
            clean_response[key.snake_name] = value
        else:
            clean_response[key] = value

    return json.dumps(clean_response)
