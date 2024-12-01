from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from local_stage import save_local_stage
from models.models import Alta, Paciente
from database import SessionLocal, engine, Base
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.exc import OperationalError, DatabaseError


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

# Esquema Pydantic para a resposta de Alta
class AltaResponse(BaseModel):
    id_alta: int
    data_hora_alta: datetime
    motivo_alta: str
    cpf: str  # CPF do paciente relacionado à alta

    class Config:
        orm_mode = True

# Esquema Pydantic para criação de Alta
class AltaCreate(BaseModel):
    data_hora_alta: datetime
    motivo_alta: str
    cpf: str  # CPF do paciente relacionado à alta

# Rota para obter todas as altas
@router.get("/", response_model=List[AltaResponse])
def get_altas(db: Session = Depends(get_db)):
    """Retorna todas as altas cadastradas."""
    altas = db.query(Alta).all()
    return altas

# Rota para obter todas as altas de um paciente pelo CPF
@router.get("/paciente/{cpf}", response_model=List[AltaResponse])
def get_altas_by_cpf(cpf: str, db: Session = Depends(get_db)):
    """Retorna todas as altas relacionadas a um paciente pelo CPF."""
    paciente = db.query(Paciente).filter(Paciente.cpf == cpf).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")

    altas = db.query(Alta).filter(Alta.cpf == cpf).all()
    if not altas:
        raise HTTPException(status_code=404, detail="Nenhuma alta encontrada para este paciente.")
    return altas

# Rota para criar uma nova alta
@router.post("/", response_model=AltaResponse)
def create_alta(alta: AltaCreate, db: Session = Depends(get_db)):
    """Cria uma nova alta."""
    # Verifica se o paciente existe
    try:
        paciente = db.query(Paciente).filter(Paciente.cpf == alta.cpf).first()
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    
        # Cria a alta
        db_alta = Alta(**alta.model_dump())
        db.add(db_alta)
        db.commit()
        db.refresh(db_alta)
        return db_alta
    except OperationalError as err:
        print("Erro de conexão com o banco de dados:", err)
        
        save_local_stage(partition_key="alta",
                         action="create",
                         data=alta.model_dump())
        raise HTTPException(status_code=503, detail="Erro de conexão com o banco de dados")
    except DatabaseError as err:
        print("Erro no servidor do banco de dados:", err)
        
        save_local_stage(partition_key="alta",
                         action="create",
                         data=alta.model_dump())
        raise HTTPException(status_code=500, detail="Erro no servidor do banco de dados")
    except Exception as err:
        print("Erro inesperado:", err)
        raise err

# Rota para obter uma alta pelo ID
@router.get("/{id_alta}", response_model=AltaResponse)
def get_alta_by_id(id_alta: int, db: Session = Depends(get_db)):
    """Retorna uma alta pelo ID."""
    alta = db.query(Alta).filter(Alta.id_alta == id_alta).first()
    if not alta:
        raise HTTPException(status_code=404, detail="Alta não encontrada.")
    return alta

# Rota para deletar uma alta pelo ID
@router.delete("/{id_alta}")
def delete_alta(id_alta: int, db: Session = Depends(get_db)):
    """Deleta uma alta pelo ID."""
    alta = db.query(Alta).filter(Alta.id_alta == id_alta).first()
    if not alta:
        raise HTTPException(status_code=404, detail="Alta não encontrada.")
    db.delete(alta)
    db.commit()
    return {"message": "Alta deletada com sucesso."}