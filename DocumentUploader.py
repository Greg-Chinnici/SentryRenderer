import boto3
import pathlib
from pathlib import Path
import time
import dotenv




class S3Client:
    def __init__(self,  envPath:str=".env"):
        env_vars = dotenv.dotenv_values(envPath)

        self.s3 = boto3.client(
            "s3",
            endpoint_url=f"https://{env_vars['ACCOUNT_ID']}.r2.cloudflarestorage.com",
            aws_access_key_id=env_vars["ACCESS_KEY"],
            aws_secret_access_key=env_vars["SECRET"],
            region_name="auto",
        )

    def Upload(self, path: Path , severity: str = None):
        bucket_name = 'DocsStorage'
        file_path = pathlib.Path(path)
        date = time.strftime("%Y%m%d-%H%M%S", time.localtime()) #! Change this datetime to the time in Sentry
        file_name = file_path.name + file_path.suffix
        r2Path = f"v1/Report-{date}/{file_name}"
    
        match path.suffix:
            case ".pdf":
                extraArgs = { 'ContentType': 'application/pdf' }
                extraArgs["ContentDisposition"] = "inline"
            case ".json":
                extraArgs = { 'ContentType': 'application/json' }
            case ".md":
                extraArgs = { 'ContentType': 'text/markdown' }
            case _:
                extraArgs = { 'ContentType': 'application/octet-stream' }
                
        self.s3.upload_file(file_path, bucket_name, r2Path, ExtraArgs=extraArgs)
        return f"{self.s3.meta.endpoint_url}/{bucket_name}/{r2Path}"