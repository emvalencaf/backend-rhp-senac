# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de conexão com o banco de dados PostgreSQL
engine = create_engine('postgresql://Rhp_owner:XgloM2KxnR0F@ep-noisy-art-a58xa0gx.us-east-2.aws.neon.tech/Rhp?sslmode=require')

# Criação da sessão de banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()
