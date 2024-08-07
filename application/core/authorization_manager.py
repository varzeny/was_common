# authorization_manager.py

## lib
import jwt, bcrypt
from datetime import datetime, timedelta, timezone
from fastapi.requests import Request
from fastapi.responses import Response
from typing import Dict, Union

## definition
class AuthorizationManager:
    secret_key = None
    algorithm = None
    expired = None
    token_type = [ "admin","user","guest" ]

    @classmethod
    def activate(cls, config:dict):
        cls.secret_key = config["secret_key"]
        cls.algorithm = config["algorithm"]
        cls.expired_min = config["expired"]


    # jwt token #############################################################
    @classmethod
    def create_token(cls, data:dict, expired_min:float):
        exp = datetime.now(timezone.utc) + timedelta(minutes=expired_min)
        data["exp"]=exp.timestamp()
        encoded_jwt = jwt.encode(
            payload=data,
            key=cls.secret_key,
            algorithm=cls.algorithm
        )
        return encoded_jwt

    @classmethod
    def verify_token(cls, token:str) -> Union[Dict, None]:
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
    def delete_token(cls, resp:Response, name:str):
        try:
            resp.delete_cookie( key=name )
            return resp
        except Exception as e:
            print("error from delete_token : ", e)

    @classmethod
    def check_token(cls, req:Request, name:str)->Union[str, None]:
        try:
            token = req.cookies.get( name )
            if token:
                decoded_token = cls.verify_token( token )
                if decoded_token:
                    return decoded_token
            print("no token")
            return None
        except Exception as e:
            print( "error from check_token : ", e )
            return None        
    

    # pw hash #############################################################
    @classmethod
    def verify_hash(cls, input_val:str, hashed_val:str ) -> str:
        return bcrypt.checkpw(
            password=input_val.encode("utf-8"),
            hashed_password=hashed_val.encode("utf-8")
        )

    @classmethod
    def create_hash(cls, input_val:str) -> str:
        result = bcrypt.hashpw(
            password= input_val.encode("utf-8"), 
            salt= bcrypt.gensalt()
        )
        return result.decode("utf-8")
    

