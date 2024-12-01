from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from local_stage import save_local_stage
from models.models import Transferencia, Paciente, Leito
from database import SessionLocal, engine, Base
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.exc import OperationalError, DatabaseError

router = APIRouter(prefix="/transferencia", tags=["Transferencia"])

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Dependência que fornece uma sessão de banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Esquema Pydantic para a resposta de Transferência
class TransferenciaResponse(BaseModel):
    id_transferencia: int
    cpf: str
    codigo_leito_origem: int
    codigo_leito_destino: int
    datahora_transferencia: datetime

    class Config:
        orm_mode = True

# Esquema Pydantic para criação de Transferência
class TransferenciaCreate(BaseModel):
    cpf: str
    codigo_leito_origem: int
    codigo_leito_destino: int
    datahora_transferencia: datetime

# Esquema Pydantic para atualização de Transferência
class TransferenciaUpdate(BaseModel):
    cpf: Optional[str] = None
    codigo_leito_origem: Optional[int] = None
    codigo_leito_destino: Optional[int] = None
    datahora_transferencia: Optional[datetime] = None

    class Config:
        orm_mode = True

@router.get("/", response_model=List[TransferenciaResponse])
def get_transferencias(db: Session = Depends(get_db)):
    """Retorna todas as transferências cadastradas."""
    transferencias = db.query(Transferencia).all()
    return transferencias

@router.post("/", response_model=TransferenciaResponse)
def create_transferencia(transferencia: TransferenciaCreate, db: Session = Depends(get_db)):
    try:
        """Cria uma nova transferência."""
        # Verifica se o paciente existe
        paciente = db.query(Paciente).filter(Paciente.cpf == transferencia.cpf).first()
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente não encontrado.")
        
        # Verifica se o leito de origem existe
        leito_origem = db.query(Leito).filter(Leito.id_leito == transferencia.codigo_leito_origem).first()
        if not leito_origem:
            raise HTTPException(status_code=404, detail="Leito de origem não encontrado.")

        # Verifica se o leito de destino existe
        leito_destino = db.query(Leito).filter(Leito.id_leito == transferencia.codigo_leito_destino).first()
        if not leito_destino:
            raise HTTPException(status_code=404, detail="Leito de destino não encontrado.")
        
        # Cria a transferência
        db_transferencia = Transferencia(**transferencia.model_dump())
        db.add(db_transferencia)
        db.commit()
        db.refresh(db_transferencia)
        return db_transferencia
    except OperationalError as err:
        print("Erro de conexão com o banco de dados:", err)
        
        save_local_stage(partition_key="transferencia",
                         action="create",
                         data=transferencia.model_dump())
        
        raise HTTPException(status_code=503, detail="Erro de conexão com o banco de dados")
    except DatabaseError as err:
        print("Erro no servidor do banco de dados:", err)
        
        save_local_stage(partition_key="transferencia",
                         action="create",
                         data=transferencia.model_dump())
        
        raise HTTPException(status_code=500, detail="Erro no servidor do banco de dados")
    except Exception as err:
        print("Erro inesperado:", err)
        raise err

@router.get("/{id_transferencia}", response_model=TransferenciaResponse)
def get_transferencia_by_id(id_transferencia: int, db: Session = Depends(get_db)):
    """Retorna uma transferência pelo ID."""
    transferencia = db.query(Transferencia).filter(Transferencia.id_transferencia == id_transferencia).first()
    if not transferencia:
        raise HTTPException(status_code=404, detail="Transferência não encontrada.")
    return transferencia

@router.get("/paciente/{cpf}", response_model=List[TransferenciaResponse])
def get_transferencias_by_cpf(cpf: str, db: Session = Depends(get_db)):
    """Retorna todas as transferências relacionadas a um paciente pelo CPF."""
    paciente = db.query(Paciente).filter(Paciente.cpf == cpf).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    
    transferencias = db.query(Transferencia).filter(Transferencia.cpf == cpf).all()
    if not transferencias:
        raise HTTPException(status_code=404, detail="Nenhuma transferência encontrada para este paciente.")
    return transferencias

@router.put("/{id_transferencia}", response_model=TransferenciaResponse)
def update_transferencia(id_transferencia: int, transferencia_update: TransferenciaUpdate, db: Session = Depends(get_db)):
    """Atualiza uma transferência pelo ID."""
    try:
        transferencia = db.query(Transferencia).filter(Transferencia.id_transferencia == id_transferencia).first()
        if not transferencia:
            raise HTTPException(status_code=404, detail="Transferência não encontrada.")

        # Validações para campos atualizados
        if transferencia_update.cpf:
            paciente = db.query(Paciente).filter(Paciente.cpf == transferencia_update.cpf).first()
            if not paciente:
                raise HTTPException(status_code=404, detail="Paciente não encontrado.")
        if transferencia_update.codigo_leito_origem:
            leito_origem = db.query(Leito).filter(Leito.id_leito == transferencia_update.codigo_leito_origem).first()
            if not leito_origem:
                raise HTTPException(status_code=404, detail="Leito de origem não encontrado.")
        if transferencia_update.codigo_leito_destino:
            leito_destino = db.query(Leito).filter(Leito.id_leito == transferencia_update.codigo_leito_destino).first()
            if not leito_destino:
                raise HTTPException(status_code=404, detail="Leito de destino não encontrado.")

        # Atualiza os campos fornecidos
        for field, value in transferencia_update.dict(exclude_unset=True).items():
            setattr(transferencia, field, value)
        
        db.commit()
        db.refresh(transferencia)
        return transferencia
    except OperationalError as err:
        print("Erro de conexão com o banco de dados:", err)
        
        save_local_stage(partition_key="transferencia",
                         action="update",
                         data=transferencia_update.model_dump())
        raise HTTPException(status_code=503, detail="Erro de conexão com o banco de dados")
    except DatabaseError as err:
        print("Erro no servidor do banco de dados:", err)
        
        save_local_stage(partition_key="transferencia",
                         action="update",
                         data=transferencia_update.model_dump())
        raise HTTPException(status_code=500, detail="Erro no servidor do banco de dados")
    except Exception as err:
        print("Erro inesperado:", err)
        raise err
    
@router.delete("/{id_transferencia}")
def delete_transferencia(id_transferencia: int, db: Session = Depends(get_db)):
    """Deleta uma transferência pelo ID."""
    transferencia = db.query(Transferencia).filter(Transferencia.id_transferencia == id_transferencia).first()
    if not transferencia:
        raise HTTPException(status_code=404, detail="Transferência não encontrada.")
    db.delete(transferencia)
    db.commit()
    return {"message": "Transferência deletada com sucesso."}