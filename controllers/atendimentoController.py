from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from models.models import Atendimento
from database import SessionLocal, engine, Base
from pydantic import BaseModel

router = APIRouter(prefix="/atendimento", tags=["Atendimento"])

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Dependência que fornece uma sessão de banco de dados para cada requisição
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Esquema Pydantic para ver todos os atendimentos
class AtendimentoResponse(BaseModel):
    id_atendimento: int
    data_atendimento: date
    tipo_atendimento: str
    id_paciente: int
    id_profissional: int

    class Config:
        from_attributes = True

# Esquema Pydantic para a criação de atendimento
class AtendimentoCreate(BaseModel):
    data_atendimento: date
    tipo_atendimento: str
    id_paciente: int
    id_profissional: int

# Esquema Pydantic para atualizar atendimento
class AtendimentoUpdate(BaseModel):
    data_atendimento: Optional[date] = None
    tipo_atendimento: Optional[str] = None
    id_paciente: Optional[int] = None
    id_profissional: Optional[int] = None

    class Config:
        from_attributes = True

@router.get("/", response_model=List[AtendimentoResponse])
def get_atendimentos(db: Session = Depends(get_db)):
    atendimentos = db.query(Atendimento).all()
    return atendimentos

@router.post("/", response_model=AtendimentoResponse)
def create_atendimento(atendimento: AtendimentoCreate, db: Session = Depends(get_db)):
    db_atendimento = Atendimento(**atendimento.dict())
    db.add(db_atendimento)
    db.commit()
    db.refresh(db_atendimento)
    return db_atendimento

@router.get("/{id_atendimento}", response_model=AtendimentoResponse)
def get_atendimento_by_id(id_atendimento: int, db: Session = Depends(get_db)):
    atendimento = db.query(Atendimento).filter(Atendimento.id_atendimento == id_atendimento).first()
    if atendimento is None:
        raise HTTPException(status_code=404, detail="Atendimento não encontrado")
    return atendimento

@router.delete("/{id_atendimento}")
def delete_atendimento(id_atendimento: int, db: Session = Depends(get_db)):
    atendimento = db.query(Atendimento).filter(Atendimento.id_atendimento == id_atendimento).first()
    if atendimento is None:
        raise HTTPException(status_code=404, detail="Atendimento não encontrado")
    db.delete(atendimento)
    db.commit()
    return {"message": "Atendimento deletado com sucesso"}

@router.put("/{id_atendimento}", response_model=AtendimentoResponse)
def update_atendimento(id_atendimento: int, atendimento_update: AtendimentoUpdate, db: Session = Depends(get_db)):
    atendimento = db.query(Atendimento).filter(Atendimento.id_atendimento == id_atendimento).first()
    if atendimento is None:
        raise HTTPException(status_code=404, detail="Atendimento não encontrado")
    
    for field, value in atendimento_update.dict(exclude_unset=True).items():
        setattr(atendimento, field, value)
    
    db.commit()
    db.refresh(atendimento)
    return atendimento