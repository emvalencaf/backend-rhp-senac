# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models.models import Unidade  # Importa o modelo Unidade do módulo models
from database import SessionLocal, engine, Base  # Importa a sessão e a engine do database.py
from pydantic import BaseModel

# Cria o aplicativo FastAPI
app = FastAPI()

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Dependência que fornece uma sessão de banco de dados para cada requisição
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Esquema Pydantic para resposta
class UnidadeResponse(BaseModel):
    id_unidade: int
    nome_unidade: str

    class Config:
        orm_mode = True

# Rota GET para buscar todas as unidades
@app.get("/unidades/", response_model=List[UnidadeResponse])
def get_unidades(db: Session = Depends(get_db)):
    unidades = db.query(Unidade).all()
    return unidades
