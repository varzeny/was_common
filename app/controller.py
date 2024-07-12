# controller.py

## lib
from fastapi import Depends
from fastapi.routing import APIRouter
from fastapi.requests import Request
from fastapi.responses import JSONResponse

## module
from app.core.database_manager import DatabaseManager as DB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

## definition
router = APIRouter()


## endpoint


### test
@router.get("/test")
async def get_test( ss:AsyncSession=Depends( DB.get_ss ) ):
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




@router.get("/")
async def get_root():
    return JSONResponse( content={"data":"hello!"}, status_code=200 )


### login
@router.post("/login")
async def post_login():
    print()