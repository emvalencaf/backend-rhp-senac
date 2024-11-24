from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from models.models import Profissional
from database import SessionLocal, engine, Base
from pydantic import BaseModel

router = APIRouter(prefix="/profissional", tags=["Profissional"])

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Dependência que fornece uma sessão de banco de dados para cada requisição
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Esquema Pydantic para ver todos os profissionais
class ProfissionalResponse(BaseModel):
    id_profissional: int
    nome: str
    especialidade: str
    registro_profissional: str
    telefone: str
    email: str

    class Config:
        from_attributes = True

# Esquema Pydantic para a criação de profissional
class ProfissionalCreate(BaseModel):
    nome: str
    especialidade: str
    registro_profissional: str
    telefone: str
    email: str

# Esquema Pydantic para atualizar profissional
class ProfissionalUpdate(BaseModel):
    nome: Optional[str] = None
    especialidade: Optional[str] = None
    registro_profissional: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True

@router.get("/", response_model=List[ProfissionalResponse])
def get_profissionais(db: Session = Depends(get_db)):
    profissionais = db.query(Profissional).all()
    return profissionais

@router.post("/", response_model=ProfissionalResponse)
def create_profissional(profissional: ProfissionalCreate, db: Session = Depends(get_db)):
    db_profissional = Profissional(**profissional.dict())
    db.add(db_profissional)
    db.commit()
    db.refresh(db_profissional)
    return db_profissional

@router.get("/{id_profissional}", response_model=ProfissionalResponse)
def get_profissional_by_id(id_profissional: int, db: Session = Depends(get_db)):
    profissional = db.query(Profissional).filter(Profissional.id_profissional == id_profissional).first()
    if profissional is None:
        raise HTTPException(status_code=404, detail="Profissional não encontrado")
    return profissional

@router.delete("/{id_profissional}")
def delete_profissional(id_profissional: int, db: Session = Depends(get_db)):
    profissional = db.query(Profissional).filter(Profissional.id_profissional == id_profissional).first()
    if profissional is None:
        raise HTTPException(status_code=404, detail="Profissional não encontrado")
    db.delete(profissional)
    db.commit()
    return {"message": "Profissional deletado com sucesso"}

@router.put("/{id_profissional}", response_model=ProfissionalResponse)
def update_profissional(id_profissional: int, profissional_update: ProfissionalUpdate, db: Session = Depends(get_db)):
    profissional = db.query(Profissional).filter(Profissional.id_profissional == id_profissional).first()
    if profissional is None:
        raise HTTPException(status_code=404, detail="Profissional não encontrado")
    
    for field, value in profissional_update.dict(exclude_unset=True).items():
        setattr(profissional, field, value)
    
    db.commit()
    db.refresh(profissional)
    return profissional