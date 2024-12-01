from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from local_stage import save_local_stage
from models.models import Atendimento, Paciente, Profissional
from database import SessionLocal, engine, Base
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.exc import OperationalError, DatabaseError


router = APIRouter(prefix="/atendimento", tags=["Atendimento"])

# Cria as tabelas no banco de dados (somente se necessário)
Base.metadata.create_all(bind=engine)

# Dependência para fornecer uma sessão de banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class AtendimentoResponse(BaseModel):
    id_atendimento: int
    data_hora: datetime
    tipo: str
    origem: Optional[str] = None
    convenio: Optional[str] = None
    cpf: str
    cpf_profissional: str

    class Config:
        orm_mode = True

class AtendimentoCreate(BaseModel):
    data_hora: datetime
    tipo: str
    origem: Optional[str] = None
    convenio: Optional[str] = None
    cpf: str
    cpf_profissional: str

@router.get("/", response_model=List[AtendimentoResponse])
def get_atendimentos(db: Session = Depends(get_db)):
    atendimentos = db.query(Atendimento).all()
    return atendimentos

@router.post("/", response_model=AtendimentoResponse)
def create_atendimento(atendimento: AtendimentoCreate, db: Session = Depends(get_db)):
    try:
        paciente = db.query(Paciente).filter(Paciente.cpf == atendimento.cpf).first()
        profissional = db.query(Profissional).filter(Profissional.cpf == atendimento.cpf_profissional).first()

        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente não encontrado.")
        if not profissional:
            raise HTTPException(status_code=404, detail="Profissional não encontrado.")

        db_atendimento = Atendimento(**atendimento.model_dump())
        db.add(db_atendimento)
        db.commit()
        db.refresh(db_atendimento)
        return db_atendimento
    except OperationalError as err:
        print("Erro de conexão com o banco de dados:", err)
        
        save_local_stage(partition_key="atendimento",
                         action="create",
                         data=atendimento.model_dump())
        raise HTTPException(status_code=503, detail="Erro de conexão com o banco de dados")
    except DatabaseError as err:
        print("Erro no servidor do banco de dados:", err)
        
        save_local_stage(partition_key="atendimento",
                         action="create",
                         data=atendimento.model_dump())
        raise HTTPException(status_code=500, detail="Erro no servidor do banco de dados")
    except Exception as err:
        print("Erro inesperado:", err)
        raise err

@router.get("/{id_atendimento}", response_model=AtendimentoResponse)
def get_atendimento_by_id(id_atendimento: int, db: Session = Depends(get_db)):
    atendimento = db.query(Atendimento).filter(Atendimento.id_atendimento == id_atendimento).first()
    if not atendimento:
        raise HTTPException(status_code=404, detail="Atendimento não encontrado.")
    return atendimento

@router.delete("/{id_atendimento}")
def delete_atendimento(id_atendimento: int, db: Session = Depends(get_db)):
    atendimento = db.query(Atendimento).filter(Atendimento.id_atendimento == id_atendimento).first()
    if not atendimento:
        raise HTTPException(status_code=404, detail="Atendimento não encontrado.")
    db.delete(atendimento)
    db.commit()
    return {"message": "Atendimento deletado com sucesso."}
