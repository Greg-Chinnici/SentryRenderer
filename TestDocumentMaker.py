from documentMaker import CreateDocuments
import logging
logging.basicConfig(level=logging.INFO)


data = {
    "hello": "world",
    "value": 42,
    "some_list": [1, 2, 3, 4, 5],
    "another_dict" : {
        "nested_key": "nested_value",
        "nested_number": 100
    }
}

CreateDocuments(data)