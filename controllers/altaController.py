from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from models.models import Alta, Paciente
from database import SessionLocal, engine, Base
from pydantic import BaseModel

router = APIRouter(prefix="/alta", tags=["Alta"])

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Dependência que fornece uma sessão de banco de dados para cada requisição
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Esquema Pydantic para ver todas as altas
class AltaResponse(BaseModel):
    id_alta: int
    data_alta: date
    motivo_alta: str
    id_paciente: int

    class Config:
        from_attributes = True

# Esquema Pydantic para a criação de alta
class AltaCreate(BaseModel):
    data_alta: date
    motivo_alta: str
    id_paciente: int

# Esquema Pydantic para atualizar alta
class AltaUpdate(BaseModel):
    data_alta: Optional[date] = None
    motivo_alta: Optional[str] = None
    id_paciente: Optional[int] = None

    class Config:
        from_attributes = True

@router.get("/", response_model=List[AltaResponse])
def get_altas(db: Session = Depends(get_db)):
    altas = db.query(Alta).all()
    return altas

@router.post("/", response_model=AltaResponse)
def create_alta(alta: AltaCreate, db: Session = Depends(get_db)):
    db_alta = Alta(**alta.dict())
    db.add(db_alta)
    db.commit()
    db.refresh(db_alta)
    return db_alta

@router.get("/{id_alta}", response_model=AltaResponse)
def get_alta_by_id(id_alta: int, db: Session = Depends(get_db)):
    alta = db.query(Alta).filter(Alta.id_alta == id_alta).first()
    if alta is None:
        raise HTTPException(status_code=404, detail="Alta não encontrada")
    return alta

@router.delete("/{id_alta}")
def delete_alta(id_alta: int, db: Session = Depends(get_db)):
    alta = db.query(Alta).filter(Alta.id_alta == id_alta).first()
    if alta is None:
        raise HTTPException(status_code=404, detail="Alta não encontrada")
    db.delete(alta)
    db.commit()
    return {"message": "Alta deletada com sucesso"}

@router.put("/{id_alta}", response_model=AltaResponse)
def update_alta(id_alta: int, alta_update: AltaUpdate, db: Session = Depends(get_db)):
    alta = db.query(Alta).filter(Alta.id_alta == id_alta).first()
    if alta is None:
        raise HTTPException(status_code=404, detail="Alta não encontrada")
    
    for field, value in alta_update.dict(exclude_unset=True).items():
        setattr(alta, field, value)
    
    db.commit()
    db.refresh(alta)
    return alta