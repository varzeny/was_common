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
        now = datetime.now(timezone.utc)
        remain_now = None

        access_token = req.cookies.get("access_token")
        if access_token:
            decoded_token = AUTH.verify_token( token=access_token )
            if decoded_token:
                ###############################
                vt = decoded_token['exp']
                exp_t = datetime.fromtimestamp( vt, timezone.utc )
                remain_now = exp_t - datetime.now(timezone.utc)
                ###############################

                decoded_token["exp"] = datetime.now(timezone.utc)+timedelta(AUTH.expired)
                req.state.token = decoded_token
       
            else: # 토큰은 있는데 유효하지 않음
                req.state.token = {"type":"guest", "name":"unknown"}             
            
        else: # 토큰이 없으면
            req.state.token = {"type":"guest", "name":"unknown"}

        print(f"========================================== {req.state.token['type']} Type Client {req.state.token['name']} ==========================================")

        # 응답 후
        resp:Response = await call_next(req)
        encoded_token = AUTH.create_token( req.state.token )
        resp.set_cookie(
            key="access_token",
            value=encoded_token,
            httponly=True,
            max_age=3600,
            path="/"
        )
        return resp
