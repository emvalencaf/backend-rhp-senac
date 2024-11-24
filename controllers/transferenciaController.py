from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from models.models import Transferencia
from database import SessionLocal, engine, Base
from pydantic import BaseModel

router = APIRouter(prefix="/transferencia", tags=["Transferencia"])

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Dependência que fornece uma sessão de banco de dados para cada requisição
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Esquema Pydantic para ver todas as transferências
class TransferenciaResponse(BaseModel):
    id_transferencia: int
    id_paciente: int
    id_leito_origem: int
    id_leito_destino: int
    data_transferencia: date
    motivo: str

    class Config:
        from_attributes = True

# Esquema Pydantic para a criação de transferência
class TransferenciaCreate(BaseModel):
    id_paciente: int
    id_leito_origem: int
    id_leito_destino: int
    data_transferencia: date
    motivo: str

# Esquema Pydantic para atualizar transferência
class TransferenciaUpdate(BaseModel):
    id_paciente: Optional[int] = None
    id_leito_origem: Optional[int] = None
    id_leito_destino: Optional[int] = None
    data_transferencia: Optional[date] = None
    motivo: Optional[str] = None

    class Config:
        from_attributes = True

@router.get("/", response_model=List[TransferenciaResponse])
def get_transferencias(db: Session = Depends(get_db)):
    transferencias = db.query(Transferencia).all()
    return transferencias

@router.post("/", response_model=TransferenciaResponse)
def create_transferencia(transferencia: TransferenciaCreate, db: Session = Depends(get_db)):
    db_transferencia = Transferencia(**transferencia.dict())
    db.add(db_transferencia)
    db.commit()
    db.refresh(db_transferencia)
    return db_transferencia

@router.get("/{id_transferencia}", response_model=TransferenciaResponse)
def get_transferencia_by_id(id_transferencia: int, db: Session = Depends(get_db)):
    transferencia = db.query(Transferencia).filter(Transferencia.id_transferencia == id_transferencia).first()
    if transferencia is None:
        raise HTTPException(status_code=404, detail="Transferência não encontrada")
    return transferencia

@router.delete("/{id_transferencia}")
def delete_transferencia(id_transferencia: int, db: Session = Depends(get_db)):
    transferencia = db.query(Transferencia).filter(Transferencia.id_transferencia == id_transferencia).first()
    if transferencia is None:
        raise HTTPException(status_code=404, detail="Transferência não encontrada")
    db.delete(transferencia)
    db.commit()
    return {"message": "Transferência deletada com sucesso"}

@router.put("/{id_transferencia}", response_model=TransferenciaResponse)
def update_transferencia(id_transferencia: int, transferencia_update: TransferenciaUpdate, db: Session = Depends(get_db)):
    transferencia = db.query(Transferencia).filter(Transferencia.id_transferencia == id_transferencia).first()
    if transferencia is None:
        raise HTTPException(status_code=404, detail="Transferência não encontrada")
    
    for field, value in transferencia_update.dict(exclude_unset=True).items():
        setattr(transferencia, field, value)
    
    db.commit()
    db.refresh(transferencia)
    return transferencia