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
from application.core.database_manager import DatabaseManager as DB
from application.schema.endpoint_schema import LoginSchema, EmailSchema
from application.core.authorization_manager import AuthorizationManager as AUTH
from application.core.email_manager import EmailManager as EM

## definition
router = APIRouter()
template = Jinja2Templates(directory="application/template")

## endpoint


### test
@router.get("/test")
async def test( req:Request ):
    print()



### widget
@router.get("/widget-account")
async def get_accountbar(req:Request):
    referer = req.headers.get("referer")
    access_token = req.state.access_token
    return template.TemplateResponse(
        name="widget_account.html",
        status_code=200,
        context={
            "request":req,
            "referer":referer,
            "access_token":access_token
        }
    )


### page
@router.get("/page-login")
async def get_page_login(req:Request):
    referer = req.query_params.get("referer")
    return template.TemplateResponse( "page_login.html", {"request":req, "referer":referer} )

@router.get("/page-sign")
async def get_page_sign(req:Request):
    access_token=req.state.access_token
    # 로그인 했으면 회원가입 하려는 요청 거르기
    if access_token["type"] != "guest":
        return {"detail":"you already have an account"}
    resp = template.TemplateResponse(
        request=req,
        name="page_sign.html",
        status_code=200,
        context={}
    )
    return resp

@router.get("/page-mypage")
async def get_mypage(req:Request):
    print()

    

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
        req.state.access_token = {
            "id":user["id_"],
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
    req.state.access_token={ "type":"guest", "name":"unknown" }
    return resp



@router.post("/sign")
async def post_sign( req:Request ):
    # 로그인을 했으면 배제
    if req.state.access_token["type"] != "guest":
        return {"detail":"you already have an account"}
    
    # 몇단계 요청인지 확인
    data = await req.json()
    step = req.query_params.get("step")

    # 단계에 맞는 쿠리를 가지고 있는지 확인
    decoded_sign_token = AUTH.check_token(req, "sign_token")
    print( decoded_sign_token )

    if step == "0": # 이메일
        print("step : ", 0)
        try :
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
                to=data["email"],
                subject="verification code is arrived",
                subtype="html",
                body=email_content
            )
            resp = JSONResponse( content={"detail":"sent email"}, status_code=200 )
            resp.set_cookie(
                key="sign_token",
                value=AUTH.create_token(
                    {
                        "step":1, 
                        "email":data["email"], 
                        "verification_code":verification_code
                    },
                    5.0
                ),
                httponly=True,
                max_age=300,
                path="/"
            )
            return resp
        except Exception as e:
            print("error from post_sign step 0 : ",e)
            return JSONResponse( content={"detail":"error"}, status_code=400 )

        
    elif step == "1": # 코드
        print("step : ",1)
        try:
            if decoded_sign_token["step"] != 1:
                return JSONResponse( content={"detail":"wrong sequence"}, status_code=400 )
            
            # 클라이언트가 보낸 코드가 맞는지 확인
            if int(data["code"]) != decoded_sign_token["verification_code"]:
                return JSONResponse( content={"detail":"wrong code"}, status_code=400 )
            
            # 쿠키를 다음 단계로
            resp = JSONResponse( content={}, status_code=200 )
            decoded_sign_token["step"] = 2
            resp.set_cookie(
                key="sign_token",
                value=AUTH.create_token( decoded_sign_token, 5.0 ),
                httponly=True,
                max_age=300,
                path="/"
            )
            return resp
        except Exception as e:
            print("error from post_sign step 1 : ",e)
            return JSONResponse( content={"detail":"error"}, status_code=400 )


    elif step == "2": # 이름
        try:
            async with DB.databases["db_1"].get_ss() as ss:
                result = await ss.execute(
                    statement=text(
                        "SELECT * FROM account WHERE name_=:name;"
                    ),
                    params={"name":data["name"]}
                )
                user = await result.fetchone()
                if user: # 이미 있는 이름이면
                    return JSONResponse(content={"detail":"that name is already exsit"}, status_code=400)
            
            decoded_sign_token["step"]=3
            decoded_sign_token["name"]=data["name"]
            resp = JSONResponse(content={},status_code=200)
            resp.set_cookie(
                key="sign_token",
                value=AUTH.create_token( decoded_sign_token, 5.0 ),
                httponly=True,
                max_age=300,
                path="/"
            )
            return resp
        except Exception as e:
            print("error from post_sign step 2 : ", e)
            return JSONResponse( content={"detail":"error"}, status_code=400 )


    elif step == "3": # 등록
        try:
            async with DB.databases["db_1"].get_ss() as ss:
                result = await ss.execute(
                    statement=text(
                        "INSERT INTO account(type_, name_, hashed_password_, email_) VALUES(:type, :name, :hashed_password, :email);"
                    ),
                    params={
                        "type":"user",
                        "name":decoded_sign_token["name"],
                        "hashed_password":AUTH.create_hash(data["password"]),
                        "email":decoded_sign_token["email"]
                    }
                )
                print(result)
                await ss.commit()
            resp = JSONResponse( content={}, status_code=200 )
            resp.delete_cookie( "sign_token" )
            return resp

        except Exception as e:
            print("error from post_sign : ", e)
            return JSONResponse( content={"detail":"error"}, status_code=400 )

