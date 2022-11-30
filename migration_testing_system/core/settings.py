from typing import Dict, Any, Optional
import json

import boto3

from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    ENV: str
    
    POSTGRES_DSN: str = None
    
    @validator("POSTGRES_DSN", pre=False)
    def assemble_postgres_dsn(self, v: Optional[str], values: Dict[str, Any]) -> str:
        if isinstance(v, str):
            return v
        
        env = values.get("ENV")
        
        client = boto3.client(service_name="secretsmanager", region_name="ap-south-1")
        response = client.get_secret_value(SecretId=f"{env}/optimization/dsn")
        secrets = json.loads(response["SecretString"])
       
        return secrets.get("optimization_dsn")
    


settings = Settings()





