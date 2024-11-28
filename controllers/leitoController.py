from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from models.models import Leito, Unidade
from database import SessionLocal, engine, Base
from pydantic import BaseModel

router = APIRouter(prefix="/leito", tags=["Leito"])

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Dependência que fornece uma sessão de banco de dados para cada requisição
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class LeitoResponse(BaseModel):
    id_leito: int
    unidade_internacao: str
    id_unidade: int

    class Config:
        orm_mode = True

class LeitoCreate(BaseModel):
    unidade_internacao: str
    id_unidade: int

class LeitoUpdate(BaseModel):
    unidade_internacao: Optional[str] = None
    id_unidade: Optional[int] = None

    class Config:
        orm_mode = True

@router.get("/", response_model=List[LeitoResponse])
def get_leitos(db: Session = Depends(get_db)):
    leitos = db.query(Leito).all()
    return leitos

@router.post("/", response_model=LeitoResponse)
def create_leito(leito: LeitoCreate, db: Session = Depends(get_db)):
    # Verifica se a unidade existe
    unidade = db.query(Unidade).filter(Unidade.id_unidade == leito.id_unidade).first()
    if not unidade:
        raise HTTPException(status_code=404, detail="Unidade não cadastrada.")
    
    # Cria o leito se a unidade existir
    db_leito = Leito(**leito.dict())
    db.add(db_leito)
    db.commit()
    db.refresh(db_leito)
    return db_leito

@router.get("/{id_leito}", response_model=LeitoResponse)
def get_leito_by_id(id_leito: int, db: Session = Depends(get_db)):
    leito = db.query(Leito).filter(Leito.id_leito == id_leito).first()
    if not leito:
        raise HTTPException(status_code=404, detail="Leito não encontrado.")
    return leito

@router.put("/{id_leito}", response_model=LeitoResponse)
def update_leito(id_leito: int, leito_update: LeitoUpdate, db: Session = Depends(get_db)):
    # Verifica se o leito existe
    leito = db.query(Leito).filter(Leito.id_leito == id_leito).first()
    if not leito:
        raise HTTPException(status_code=404, detail="Leito não encontrado.")

    # Verifica se o id_unidade atualizado é válido, se foi fornecido
    if leito_update.id_unidade:
        unidade = db.query(Unidade).filter(Unidade.id_unidade == leito_update.id_unidade).first()
        if not unidade:
            raise HTTPException(status_code=404, detail="Unidade não cadastrada.")

    # Atualiza os campos informados
    for field, value in leito_update.dict(exclude_unset=True).items():
        setattr(leito, field, value)

    db.commit()
    db.refresh(leito)
    return leito

@router.delete("/{id_leito}")
def delete_leito(id_leito: int, db: Session = Depends(get_db)):
    leito = db.query(Leito).filter(Leito.id_leito == id_leito).first()
    if not leito:
        raise HTTPException(status_code=404, detail="Leito não encontrado.")
    db.delete(leito)
    db.commit()
    return {"message": "Leito deletado com sucesso."}