# controller.py

## lib
from fastapi import Depends
from fastapi.routing import APIRouter
from fastapi.requests import Request
from fastapi.responses import JSONResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import random

## module
from app.core.database_manager import DatabaseManager as DB
from app.schema.endpoint_schema import LoginSchema, EmailSchema
from app.core.authorization_manager import AuthorizationManager as AUTH
from app.core.email_manager import EmailManager as EM

## definition
router = APIRouter()
template = Jinja2Templates(directory="app/template")

## endpoint


### test
@router.get("/test")
async def test( req:Request ):
    print()



### widget
@router.get("/widget-account")
async def get_accountbar(req:Request):
    referer = req.headers.get("referer")
    token = req.state.token
    return template.TemplateResponse(
        name="widget_account.html",
        status_code=200,
        context={
            "request":req,
            "referer":referer,
            "token":token
        }
    )


### page
@router.get("/page-login")
async def get_page_login(req:Request):
    referer = req.query_params.get("referer")
    return template.TemplateResponse( "page_login.html", {"request":req, "referer":referer} )

@router.get("/page-sign")
async def get_page_sign(req:Request):
    token=req.state.token
    # 로그인 했으면 회원가입 하려는 요청 거르기
    if token:
        return {"detail":"you already login"}

    referer = req.query_params.get("referer")
    sign_token = req.cookies.get( "sign_token" )
    if not sign_token:
        AUTH
    return template.TemplateResponse(
        request=req,
        name="page_sign.html",
        context={
            "referer":referer,
            "step":sign_token["step"]
        }
    )


### general
#### login
@router.post("/login")
async def post_login( req:Request, data:LoginSchema ):
    print("input data : ", type(data), data)

    async with DB.databases["db_1"].get_ss() as ss:
        result = await ss.execute(
            text("""
            SELECT * FROM account WHERE name_=:name;
            """),
            params={ "name":data.name }
        )
        user = result.mappings().first()

    if user:
        ##### pw hash
        tof = AUTH.verify_hash( 
            input_val=data.password, hashed_val=user["hashed_password_"] 
        )
        if not tof:
            return JSONResponse( status_code=404, content={} )

        ##### token
        resp = JSONResponse( status_code=200, content={} )
        req.state.token = {
            "name":user["name_"],
            "type":user["type_"]
        }
        return resp
    else:
        return JSONResponse( status_code=404, content={} )


#### logout
@router.get("/logout")
async def get_logout( req:Request ):
    referer = req.query_params.get("referer")
    resp = RedirectResponse(
        url=referer
    )
    req.state.token={ "type":"guest", "name":"unknown" }
    return resp


#### sign up
@router.post("/sign-1")
async def post_sign_1( req:Request, data:EmailSchema ):
    print(data.email)

    try:
        # duplicate check
        async with DB.databases["db_1"].get_ss() as ss:
            result = await ss.execute(
                statement=text("""
                    SELECT name_ FROM account WHERE email_=:email;
                """),
                params={
                    "email":data.email
                }
            )
            user = result.fetchone()
            print(user)
            if user:
                return JSONResponse(
                    content={"detail":"this email already exist"},
                    status_code=400
                )


        # e-mail send
        verification_code = random.randint( 10000, 99999 )
        html = template.TemplateResponse(
            name="email_form.html",
            context={
                "request":req,
                "verification_code":verification_code
            }
        )
        email_content = html.body.decode("utf-8")

        client = EM.clients["client_1"]
        await client.send_email(
            to=data.email,
            subject="verification code is arrived",
            subtype="html",
            body=email_content
        )

        # token
        sign_token = AUTH.create_token( {
            "step":2,
            "verification_code":verification_code
        } )
        resp = template.TemplateResponse(
            request=req,
            name="page_sign_2.html",
            context={}
        )
        resp.set_cookie(
            key="sign_token",
            value=sign_token,
            httponly=True,
            max_age=600,
            path="/"
        )
        return resp


    except Exception as e:
        print( "error from post_check_email : ", e )
        return JSONResponse( content={}, status_code=404 )
    



