from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = ""
engine = create_async_engine(DATABASE_URL, echo=True)

# Асинхронная сессия
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)

Base = declarative_base()
# Функция для получения асинхронной сессии
async def get_db():
    async with SessionLocal() as session:
        yield session