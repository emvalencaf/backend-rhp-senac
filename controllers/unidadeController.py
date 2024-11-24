from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from models.models import Unidade, Paciente, Leito, Transferencia, Alta, Atendimento, Profissional
from database import SessionLocal, engine, Base
from pydantic import BaseModel

router = APIRouter(prefix="/unidade", tags=["Unidade"])

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Dependência que fornece uma sessão de banco de dados para cada requisição
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Esquema Pydantic para ver todas as unidades
class UnidadeResponse(BaseModel):
    id_unidade: int
    nome_unidade: str

    class Config:
        from_attributes = True

# Esquema Pydantic para a criação de unidade
class UnidadeCreate(BaseModel):
    nome_unidade: str

# Esquema Pydantic para atualizar unidade
class UnidadeUpdate(BaseModel):
    nome_unidade: Optional[str] = None

    class Config:
        from_attributes = True

@router.get("/", response_model=List[UnidadeResponse])
def get_unidades(db: Session = Depends(get_db)):
    unidades = db.query(Unidade).all()
    return unidades

@router.post("/", response_model=UnidadeResponse)
def create_unidade(unidade: UnidadeCreate, db: Session = Depends(get_db)):
    db_unidade = Unidade(nome_unidade=unidade.nome_unidade)
    db.add(db_unidade)
    db.commit()
    db.refresh(db_unidade)
    return db_unidade

@router.get("/{id_unidade}", response_model=UnidadeResponse)
def get_unidade_by_id(id_unidade: int, db: Session = Depends(get_db)):
    unidade = db.query(Unidade).filter(Unidade.id_unidade == id_unidade).first()
    if unidade is None:
        raise HTTPException(status_code=404, detail="Unidade não encontrada")
    return unidade

@router.delete("/{id_unidade}")
def delete_unidade(id_unidade: int, db: Session = Depends(get_db)):
    unidade = db.query(Unidade).filter(Unidade.id_unidade == id_unidade).first()
    if unidade is None:
        raise HTTPException(status_code=404, detail="Unidade não encontrada")
    db.delete(unidade)
    db.commit()
    return {"message": "Unidade deletada com sucesso"}

@router.put("/{id_unidade}", response_model=UnidadeResponse)
def update_unidade(id_unidade: int, unidade_update: UnidadeUpdate, db: Session = Depends(get_db)):
    unidade = db.query(Unidade).filter(Unidade.id_unidade == id_unidade).first()
    if unidade is None:
        raise HTTPException(status_code=404, detail="Unidade não encontrada")
    
    if unidade_update.nome_unidade:
        unidade.nome_unidade = unidade_update.nome_unidade
    
    db.commit()
    db.refresh(unidade)
    return unidade