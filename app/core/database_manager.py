# database_manager.py

## lib
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from contextlib import asynccontextmanager
from typing import Dict
## module

## definition

class Database:
    def __init__( self, config ) -> None:
        self.name = config["name"]
        self.url = config["url"]
        self.state = "deactive"
        self.engine = None
        self.session = None

    def activate(self):
        self.engine = create_async_engine(
            url = self.url
        )
        self.session = async_sessionmaker(
            bind = self.engine,
            expire_on_commit = False,
            class_=AsyncSession
        )
        self.state = "active"

    async def deactivate(self):
        await self.engine.dispose()
        self.session = None
        self.engine = None
        self.state = "deactive"

    @asynccontextmanager
    async def get_ss(self):
        try:
            ss = self.session()
            yield ss
        except Exception as e:
            print(f"error from get_ss of {self.name}")
        finally:
            await ss.close()


class DatabaseManager:
    databases:Dict[str, Database] = {}

    @classmethod
    def add_database( cls, config ):
        cls.databases[ config["name"] ] = Database( config )

    @classmethod
    async def remove_database( cls, name ):
        if name == "all":
            for k, v in cls.databases.items():
                await v.deactivate()
                del k
            return
        
        await cls.databases[name].deactive()
        del cls.databases[name]

