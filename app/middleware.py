# middleware.py

# lib
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timezone, timedelta

# module
from app.core.authorization_manager import AuthorizationManager as AUTH

# definition
class AccessTokenMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, req:Request, call_next):
        now_t = datetime.now(timezone.utc)
        remain_t = None

        decoded_access_token = AUTH.check_token( req, "access_token" )
        if decoded_access_token:
            ###############################
            vt = decoded_access_token['exp']
            exp_t = datetime.fromtimestamp( vt, timezone.utc )
            remain_t = exp_t - datetime.now(timezone.utc)
            ###############################

            decoded_access_token["exp"] = datetime.now(timezone.utc)+timedelta(AUTH.expired_min)
            req.state.access_token = decoded_access_token
    
        else: # 토큰이 없으면
            req.state.access_token = {"type":"guest", "name":"unknown"}

        print(f"========================================== {req.state.access_token['type']} {req.state.access_token['name']} ==========================================")
        print(f"current time : {now_t} token remaining time : {remain_t}")

        # 응답 후
        resp:Response = await call_next(req)
        encoded_access_token = AUTH.create_token( req.state.access_token, AUTH.expired_min )
        resp.set_cookie(
            key="access_token",
            value=encoded_access_token,
            httponly=True,
            max_age=3600,
            path="/"
        )
        return resp
