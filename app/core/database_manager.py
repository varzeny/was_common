# database_manager.py

## lib
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

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
        cls.async_session = sessionmaker(
            cls.async_engine,
            expire_on_commit=False,
            class_=AsyncSession
        )
        print("DB statup done!")

    
    @classmethod
    async def get_ss(cls):
        try:
            ss = cls.async_session()
            yield ss
        except Exception as e:
            print("error : ",e)
            await ss.rollback()
        finally:
            await ss.close()
