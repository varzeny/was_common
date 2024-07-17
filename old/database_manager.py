# database_manager.py

## lib
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from contextlib import asynccontextmanager

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

    # async def get_ss(self):
    #     try:
    #         ss = self.session()
    #         yield ss
    #     except Exception as e:
    #         print(f"error from get_ss of {self.name}")
    #     finally:
    #         await ss.close()


class DatabaseManager:
    databases = {}

    @classmethod
    def add_database( cls, config ):
        cls.databases[ config["name"] ] = Database( config )

    @classmethod
    async def remove_database( cls, name ):
        await cls.databases[name].deactive()
        del cls.databases[name]


    # dependencies #######################
    # Depends 의 병신같은 구조 때문에 엔드포인트에서 with 문 쓰기 싫으면 이딴식으로 해야함
    # Depends 는 url 자체에 매개변수가 있는게 아니면 매개변수를 줄 방법이 없음. 람다 쓰면 반환 자료형이 달라짐 
    # DB 객체를 추가할때마다 그 DB와의 연결을 반환하는 고유한 이름의 함수를 정의하고 Depends() 에서 사용할것
    # 앱 시작시에 Depends() 내부에 배치한 함수들을 찾아서 연결해두는 방식 같음. 그래서 나중에 동적으로 바꿀수 있는 각이 안보임
    # 시발 그래봐야 개미 좇물만큼 빨라질텐 그냥 엔드포인트에서 with 문 쓰는게 나은것 같기도 함
    # 이새끼들은 복수의 DB를 바꿔가면서 쓸거라는 생각을 아예 안한건가?
    @classmethod
    async def get_db_1(cls):
        try:
            ss = cls.databases["db_1"].session()
            yield ss
        except Exception as e:
            print("error from get_db_1 : ",e)
        finally:
            await ss.close()










# class DatabaseManager:
#     url = None
#     async_engine = None
#     async_session = None

#     @classmethod
#     def activate( cls, data:dict ):
#         cls.url = data["url"]
#         cls.async_engine = create_async_engine(
#             url=cls.url,
#             pool_size = 10
#         )
#         cls.async_session = sessionmaker(
#             cls.async_engine,
#             expire_on_commit=False,
#             class_=AsyncSession
#         )
#         print("DB statup done!")

    
#     @classmethod
#     async def get_ss(cls):
#         try:
#             ss = cls.async_session()
#             yield ss
#         except Exception as e:
#             print("error : ",e)
#             await ss.rollback()
#         finally:
#             await ss.close()
