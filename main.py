# main.py


## lib
import os
from fastapi import FastAPI

## module
from app.core.util_manager import read_file_for_json
from app.controller import router as r1

## definition

### startup sequence
async def startup():
    print("startup...")

    #### read config
    app.state.config = read_file_for_json( os.path.join( os.path.dirname(__file__), "config.json" ) )
    
    #### endpoint router
    app.include_router( r1 )

    print("startup done!")

### shutdown sequence
async def shutdown():
    print("shutdown...")

    print("shutdown done!")


app = FastAPI(
    on_startup=[
        startup
    ],
    on_shutdown=[
        shutdown
    ]
)


