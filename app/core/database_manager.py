# database_manager.py

## lib
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

## module

## definition

class DatabaseManager:
    url = None
    async_engine = None
    async_session = None

    @classmethod
    def activate( cls, data:dict ):
        cls.url = data["url"]
        cls.async_engine = create_async_engine(
            url=cls.url,
            pool_size = 10
        )

        print("DB statup done")

    
    @classmethod
    def get_ss(cls):
        try:
            yield cls.async_session
        except Exception as e:
            print("error : ",e)
        finally:
            