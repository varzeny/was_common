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
from app.core.authorization_manager import AuthorizationManager as AUTH

## definition
router = APIRouter()
template = Jinja2Templates(directory="app/template")

## endpoint


### test
@router.get("/test")
async def test(req:Request, ss:AsyncSession=Depends(DB.get_ss)):
    for i in range(1,11,1):
        new_pw = AUTH.create_hash("admin")
        result = await ss.execute(
            statement=text(
                "UPDATE account SET hashed_password_=:value WHERE id_=:id"
            ),
            params={
                "value":new_pw,
                "id":i
            }
        )
        print("---",result)
    await ss.commit()
    return {"data":"success"}



### widget
@router.get("/widget-account")
async def get_accountbar(req:Request, token:str=Depends(AUTH.check_token)):
    referer = req.headers.get("referer")

    if token:
        print("yes")
        print(token)
    else:
        print("no")
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
    referer = req.query_params.get("referer")
    return template.TemplateResponse( "page_sign.html", {"request":req, "referer":referer} )


### general
#### login
@router.post("/login")
async def post_login( data:LoginSchema, ss:AsyncSession=Depends( DB.get_ss ) ):
    print(type(data), data)
    
    query = """
    SELECT * FROM account WHERE name_=:name;
    """
    result = await ss.execute(
        text(query),
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
        new_token = AUTH.create_token( {
            "name":user["name_"],
            "type":user["type_"]
        } )

        ##### httponly 쿠키에 토큰 넣어주기
        resp.set_cookie(
            key="access_token",
            value=new_token,
            httponly=True,
            max_age=3600,
            path="/"
        )
        return resp
    else:
        print("---1")
        return JSONResponse( status_code=404, content={} )


#### logout
@router.get("/logout")
async def get_logout( req:Request ):
    referer = req.query_params.get("referer")
    resp = RedirectResponse(
        url=referer
    )
    resp.delete_cookie(key="access_token")
    return resp

#### sign up
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