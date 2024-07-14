# authorization_manager.py

## lib
import jwt
from datetime import datetime, timedelta
from fastapi.requests import Request
from fastapi.responses import Response

## definition
class AuthorizationManager:
    secret_key = None
    algorithm = None
    expired = None
    token_type = [ "admin","user","test" ]

    @classmethod
    def activate(cls, config:dict):
        cls.secret_key = config["secret_key"]
        cls.algorithm = config["algorithm"]
        cls.expired = config["expired"]

    @classmethod
    def create_token(cls, data:dict):
        exp = datetime.now() + timedelta(minutes=cls.expired)
        data["exp"]=exp
        encoded_jwt = jwt.encode(
            payload=data,
            key=cls.secret_key,
            algorithm=cls.algorithm
        )
        return encoded_jwt

    @classmethod
    def verify_token(cls, token:str):
        try:
            decoded_jwt = jwt.decode(
                jwt=token,
                key=cls.secret_key,
                algorithms=cls.algorithm
            )
            return decoded_jwt
        except jwt.ExpiredSignatureError:
            print("Token has expired")
            return None
        except jwt.InvalidTokenError:
            print("Invalid token")
            return None
        except Exception as e:
            print("error from verify_token : ",e)
            return None
        
    @classmethod
    def check_token(cls, req:Request):
        token = req.cookies.get( "access_token" )
        if not token:
            print("no token")
            return None
        
        decoded_token = cls.verify_token(token)
        if not decoded_token:
            print("token problem")
            return None
        
        return decoded_token


