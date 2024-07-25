# main.py


## lib
import os
from fastapi import FastAPI, staticfiles

## module
from application.core.util_manager import read_file_for_json
from application.middleware import AccessTokenMiddleware
from application.core.authorization_manager import AuthorizationManager
from application.core.database_manager import DatabaseManager
from application.core.email_manager import EmailManager
from application.controller import router as r1

## definition

### startup sequence
async def startup():
    print("startup...")

    #### read config
    app.state.config = read_file_for_json( os.path.join( os.path.dirname(__file__), "config.json" ) )

    #### static mount
    app.mount(
        path="/static",
        app=staticfiles.StaticFiles( directory="application/static" ),
        name="static"
    )

    #### Authorization Manager setup
    AuthorizationManager.activate( app.state.config["authorization_manager"] )

    #### DataBase Manager setup
    DatabaseManager.add_database( app.state.config["database_manager"]["db_1"] )
    DatabaseManager.databases["db_1"].activate()

    #### Email Manager setup
    EmailManager.add_client( app.state.config["email_manager"]["client_1"] )
    
    #### endpoint router
    app.include_router( r1 )

    print("startup done!")

### shutdown sequence
async def shutdown():
    print("shutdown...")

    #### DB
    await DatabaseManager.remove_database("all")

    print("shutdown done!")


app = FastAPI(
    on_startup=[
        startup
    ],
    on_shutdown=[
        shutdown
    ]
)

#### Middleware setup
app.add_middleware( AccessTokenMiddleware )
