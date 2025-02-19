from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base


engine = create_async_engine(settings.DATABASE_URL, echo=True)

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