from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from models.models import Paciente
from database import SessionLocal, engine, Base
from pydantic import BaseModel

router = APIRouter(prefix="/paciente", tags=["Paciente"])

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Dependência que fornece uma sessão de banco de dados para cada requisição
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Esquema Pydantic para ver todos os pacientes
class PacienteResponse(BaseModel):
    id_paciente: int
    nome: str
    cpf: str
    data_nascimento: date
    endereco: str
    telefone: str
    email: str

    class Config:
        from_attributes = True

# Esquema Pydantic para a criação de paciente
class PacienteCreate(BaseModel):
    nome: str
    cpf: str
    data_nascimento: date
    endereco: str
    telefone: str
    email: str

# Esquema Pydantic para atualizar paciente
class PacienteUpdate(BaseModel):
    nome: Optional[str] = None
    cpf: Optional[str] = None
    data_nascimento: Optional[date] = None
    endereco: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True

@router.get("/", response_model=List[PacienteResponse])
def get_pacientes(db: Session = Depends(get_db)):
    pacientes = db.query(Paciente).all()
    return pacientes

@router.post("/", response_model=PacienteResponse)
def create_paciente(paciente: PacienteCreate, db: Session = Depends(get_db)):
    db_paciente = Paciente(**paciente.dict())
    db.add(db_paciente)
    db.commit()
    db.refresh(db_paciente)
    return db_paciente

@router.get("/{id_paciente}", response_model=PacienteResponse)
def get_paciente_by_id(id_paciente: int, db: Session = Depends(get_db)):
    paciente = db.query(Paciente).filter(Paciente.id_paciente == id_paciente).first()
    if paciente is None:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return paciente

@router.delete("/{id_paciente}")
def delete_paciente(id_paciente: int, db: Session = Depends(get_db)):
    paciente = db.query(Paciente).filter(Paciente.id_paciente == id_paciente).first()
    if paciente is None:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    db.delete(paciente)
    db.commit()
    return {"message": "Paciente deletado com sucesso"}

@router.put("/{id_paciente}", response_model=PacienteResponse)
def update_paciente(id_paciente: int, paciente_update: PacienteUpdate, db: Session = Depends(get_db)):
    paciente = db.query(Paciente).filter(Paciente.id_paciente == id_paciente).first()
    if paciente is None:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    for field, value in paciente_update.dict(exclude_unset=True).items():
        setattr(paciente, field, value)
    
    db.commit()
    db.refresh(paciente)
    return paciente
