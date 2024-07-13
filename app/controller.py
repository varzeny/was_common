# controller.py

## lib
from fastapi import Depends
from fastapi.routing import APIRouter
from fastapi.requests import Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

## module
from app.core.database_manager import DatabaseManager as DB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.schema.endpoint_schema import LoginSchema, SignSchema

## definition
router = APIRouter()
template = Jinja2Templates(directory="app/template")

## endpoint


### test
@router.get("/test")



### sign up

@router.post("/sign")
async def post_sign( ss:AsyncSession=Depends( DB.get_ss ) ):
    name="kim"
    password="123"
    query = """
    INSERT INTO account(name, password)
    VALUES(:name, :password) AS vals
    ON DUPLICATE KEY UPDATE name=vals.name, password=vals.password
    """
    await ss.execute(
        statement=text( query ),
        params={"name":name, "password":password}
    )
    await ss.commit()




### widget
@router.get("/widget-account")
async def get_accountbar(req:Request):
    return template.TemplateResponse( "widget_account.html", {"request":req} )


### page
@router.get("/page-login")
async def get_page_login(req:Request):
    return template.TemplateResponse( "page_login.html", {"request":req} )


### general
#### login
@router.post("/login")
async def post_login( data:LoginSchema, ss:AsyncSession=Depends( DB.get_ss ) ):
    print(type(data), data)
    
    query = """
    SELECT * FROM account WHERE name_=:name AND password_=:password;
    """
    result = await ss.execute(
        text(query),
        params={ "name":data.name, "password":data.password }
    )
    results = result.all()

    if results:
        print(type(results[0]), results[0])
        resp = JSONResponse( content={}, status_code=200 )
        # 토큰 발행 구현할 것, 토큰 확인도 구현할것
        new_token = 

        # httponly 쿠키 넣어주기
        resp.set_cookie(
            key="login_token",
            value=new_token,
            httponly=True,
            max_age=3600,
            path="/"
        )
        return resp
    else:
        return JSONResponse( content={}, status_code=404 )