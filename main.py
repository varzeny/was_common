# main.py


## lib
import os
from fastapi import FastAPI

## module
from app.core.util_manager import read_file_for_json
from app.core.authorization_manager import AuthorizationManager
from app.core.database_manager import DatabaseManager
from app.controller import router as r1

## definition

### startup sequence
async def startup():
    print("startup...")

    #### read config
    application.state.config = read_file_for_json( os.path.join( os.path.dirname(__file__), "config.json" ) )

    #### Authorization Manager setup
    AuthorizationManager.activate( application.state.config["authorization_manager"] )

    #### DataBase Manager setup
    DatabaseManager.add_database( application.state.config["database_manager"]["db_1"] )
    DatabaseManager.databases["db_1"].activate()
    
    #### endpoint router
    application.include_router( r1 )

    print("startup done!")

### shutdown sequence
async def shutdown():
    print("shutdown...")

    print("shutdown done!")


application = FastAPI(
    on_startup=[
        startup
    ],
    on_shutdown=[
        shutdown
    ]
)


