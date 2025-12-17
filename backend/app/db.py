import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import text
from app.config import settings

logger = logging.getLogger(__name__)

# --- New Logic to handle DB creation ---

# 1. Get server URL and DB name from the full connection string
try:
    server_url = settings.database_url.rsplit('/', 1)[0]
    db_name = settings.database_url.split('/')[-1].split('?')[0]
except IndexError:
    logger.error("Invalid DATABASE_URL. It should be in the format 'driver://user:pass@host/database_name'")
    raise

# 2. Engine to connect to the MySQL server itself (without a specific database)
server_engine = create_async_engine(server_url, echo=settings.debug)

# 3. Engine to connect to the specific 'ai_interview' database
engine = create_async_engine(settings.database_url, echo=settings.debug)

# 4. Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 5. Create base class for ORM models
Base = declarative_base()

async def get_db() -> AsyncSession:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    """
    Initializes the database. Creates the database if it doesn't exist,
    then creates all the tables.
    """
    try:
        # 6. Connect to the server and create the database if it's not there
        async with server_engine.connect() as conn:
            await conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))
            await conn.commit()
        logger.info(f"Database '{db_name}' created or already exists.")

        # 7. Now, connect to the specific database and create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully.")

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

async def close_db():
    """Close database connections"""
    await engine.dispose()
    logger.info("Database connections closed")