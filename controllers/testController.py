from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from models.models import Unidade, Paciente, Leito, Transferencia, Alta, Atendimento, Profissional
from database import SessionLocal, engine, Base  # Importa a sessão e a engine do database.py
from pydantic import BaseModel

router = APIRouter(prefix="/test", tags=["Test"])

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Dependência que fornece uma sessão de banco de dados para cada requisição
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Exemplo de rota GET para testar a API
@router.get("/")
def test_api():
    return {"message": "API está funcionando!"}
