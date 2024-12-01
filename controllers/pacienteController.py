from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from local_stage import save_local_stage
from models.models import Paciente
from database import SessionLocal, engine, Base
from pydantic import BaseModel
from datetime import date
from sqlalchemy.exc import OperationalError, DatabaseError

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

# Esquema Pydantic para a resposta de paciente
class PacienteResponse(BaseModel):
    cpf: str
    nome: str
    data_nascimento: Optional[date] = None
    endereco: Optional[str] = None
    cep: Optional[str] = None
    nome_mae: Optional[str] = None

    class Config:
        orm_mode = True

# Esquema Pydantic para criação de paciente
class PacienteCreate(BaseModel):
    cpf: str
    nome: str
    data_nascimento: date
    endereco: Optional[str] = None
    cep: Optional[str] = None
    nome_mae: Optional[str] = None

# Esquema Pydantic para atualização de paciente
class PacienteUpdate(BaseModel):
    nome: Optional[str] = None
    data_nascimento: Optional[date] = None
    endereco: Optional[str] = None
    cep: Optional[str] = None
    nome_mae: Optional[str] = None

    class Config:
        orm_mode = True

@router.get("/", response_model=List[PacienteResponse])
def get_pacientes(db: Session = Depends(get_db)):
    """Retorna todos os pacientes cadastrados."""
    pacientes = db.query(Paciente).all()
    return pacientes

@router.post("/", response_model=PacienteResponse)
def create_paciente(paciente: PacienteCreate, db: Session = Depends(get_db)):
    """Cria um novo paciente."""
    try:
        # Verifica se o CPF já está cadastrado
        if db.query(Paciente).filter(Paciente.cpf == paciente.cpf).first():
            raise HTTPException(status_code=400, detail="CPF já cadastrado.")
        
        # Cria o paciente
        db_paciente = Paciente(**paciente.model_dump())
        db.add(db_paciente)
        db.commit()
        db.refresh(db_paciente)
        return db_paciente
    except OperationalError as err:
        print("Erro de conexão com o banco de dados:", err)
        
        save_local_stage(partition_key="paciente",
                         action="create",
                         data=paciente.model_dump())
        raise HTTPException(status_code=503, detail="Erro de conexão com o banco de dados")
    except DatabaseError as err:
        print("Erro no servidor do banco de dados:", err)
        
        save_local_stage(partition_key="paciente",
                         action="create",
                         data=paciente.model_dump())
        raise HTTPException(status_code=500, detail="Erro no servidor do banco de dados")
    except Exception as err:
        print("Erro inesperado:", err)
        raise err

@router.get("/{cpf}", response_model=PacienteResponse)
def get_paciente_by_cpf(cpf: str, db: Session = Depends(get_db)):
    """Retorna um paciente pelo CPF."""
    paciente = db.query(Paciente).filter(Paciente.cpf == cpf).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    return paciente

@router.put("/{cpf}", response_model=PacienteResponse)
def update_paciente(cpf: str, paciente_update: PacienteUpdate, db: Session = Depends(get_db)):
    """Atualiza um paciente pelo CPF."""
    try:
        paciente = db.query(Paciente).filter(Paciente.cpf == cpf).first()
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente não encontrado.")
        
        # Atualiza apenas os campos fornecidos
        for field, value in paciente_update.model_dump(exclude_unset=True).items():
            setattr(paciente, field, value)
        
        db.commit()
        db.refresh(paciente)
        return paciente
    except OperationalError as err:
        print("Erro de conexão com o banco de dados:", err)
        
        save_local_stage(partition_key="paciente",
                         action="update",
                         data=paciente_update.model_dump())
        raise HTTPException(status_code=503, detail="Erro de conexão com o banco de dados")
    except DatabaseError as err:
        print("Erro no servidor do banco de dados:", err)
        
        save_local_stage(partition_key="paciente",
                         action="update",
                         data=paciente_update.model_dump())
        raise HTTPException(status_code=500, detail="Erro no servidor do banco de dados")
    except Exception as err:
        print("Erro inesperado:", err)
        raise err


@router.delete("/{cpf}")
def delete_paciente(cpf: str, db: Session = Depends(get_db)):
    """Deleta um paciente pelo CPF."""
    paciente = db.query(Paciente).filter(Paciente.cpf == cpf).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    db.delete(paciente)
    db.commit()
    return {"message": "Paciente deletado com sucesso."}