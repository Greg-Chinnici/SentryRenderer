from documentMaker import CreateDocuments
from pathlib import Path

import logging
logging.basicConfig(level=logging.INFO ,filename="DocumentMaker.log" , filemode="w")


data = {
    "hello": "world",
    "value": 42,
    "some_list": [1, 2, 3, 4, 5],
    "another_dict" : {
        "nested_key": "nested_value",
        "nested_number": 100
    }
}

createdPaths = CreateDocuments(data , output_dir=Path.cwd() / 'exported')
if createdPaths is not None:
    for path in createdPaths:
        logging.info(f"Created file at: {Path(path).resolve()}")

    # now out of temp scope
    # can send out to emails , curl or other services
    # then delete the files