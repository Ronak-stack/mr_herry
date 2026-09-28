# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base

# engine = create_engine(
#     "mysql+pymysql://root:@localhost:3306/bot_db",
#     pool_pre_ping=True
# )

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # 3. ADD THIS LINE: This creates the missing 'Base' object Alembic is looking for
# Base = declarative_base()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine(
    "mysql+pymysql://root:@localhost:3306/bot_db",
    pool_pre_ping=True,
    pool_recycle=1800
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()