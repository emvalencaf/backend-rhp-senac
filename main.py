# main.py
from fastapi import FastAPI, Depends, HTTPException
from datetime import date
from sqlalchemy.orm import Session, joinedload
from typing import List
from local_stage import save_local_stage
from models.models import Unidade, Paciente, Leito, Transferencia, Alta, Atendimento, Profissional # Importa os models
from database import SessionLocal, engine, Base  # Importa a sessão e a engine do database.py
from pydantic import BaseModel
from sqlalchemy.exc import OperationalError, DatabaseError

# Cria o aplicativo FastAPI
app = FastAPI()

#====== Rota Publica apenas para testar no Postman se esta tudo funcionando======
@app.get("/")
def root():
    return {"message": "API esta funcionando!"}

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Dependência que fornece uma sessão de banco de dados para cada requisição
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


