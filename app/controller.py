# controller.py

## lib
from fastapi.routing import APIRouter
from fastapi.requests import Request
from fastapi.responses import JSONResponse
## module


## definition
router = APIRouter()


## endpoint


### test
@router.get("/")
async def get_root():
    return JSONResponse( content={"data":"hello!"}, status_code=200 )


### login
@router.post("/login")
async def post_login():
    print()