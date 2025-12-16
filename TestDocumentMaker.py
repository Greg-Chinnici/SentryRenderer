from documentMaker import CreateDocuments
from pathlib import Path
import sys
import logging
logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.FileHandler("DocumentMaker.log" , mode="a"), logging.StreamHandler(sys.stdout)], 
    force=True,
)

data = {
    "hello": "world",
    "value": 42,
    "some_list": [1, 2, 3, 4, 5],
    "another_dict" : {
        "nested_key": "nested_value",
        "nested_number": 100
    },
    "permalink": "https://google.com", 
}

from DocumentUploader import S3Client

S3Client = S3Client(".env")

createdPaths = CreateDocuments(data , output_dir=Path.cwd() / 'Resources')
if createdPaths is not None:
    for type , path in createdPaths.items():
        match type:
            case "markdown":
                logging.info(f"Created Markdown file at: {Path(path).resolve()}")
            case "typst":
                logging.info(f"Created Typst PDF file at: {Path(path).resolve()}")
            case "json":
                logging.info(f"Created metadata JSON file at: {Path(path).resolve()}")
            case _:
                logging.error(f"Unknown file type: {type} at path: {Path(path).resolve()}")
      
        url = S3Client.Upload(path)
        print(f"File uploaded to Cloudflare at URL: {url}")
        
    # now out of temp scope
    # can send out to emails , curl or other services
    # then delete the files