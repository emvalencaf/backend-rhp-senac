from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from local_stage import save_local_stage
from models.models import Unidade
from database import SessionLocal, engine, Base
from pydantic import BaseModel
from sqlalchemy.exc import OperationalError, DatabaseError

router = APIRouter(prefix="/unidade", tags=["Unidade"])

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Dependência que fornece uma sessão de banco de dados para cada requisição
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UnidadeResponse(BaseModel):
    id_unidade: int
    nome_unidade: str
    descricao_unid: Optional[str] = None

    class Config:
        orm_mode = True

class UnidadeCreate(BaseModel):
    nome_unidade: str
    descricao_unid: Optional[str] = None

@router.get("/", response_model=List[UnidadeResponse])
def get_unidades(db: Session = Depends(get_db)):
    unidades = db.query(Unidade).all()
    return unidades

@router.post("/", response_model=UnidadeResponse)
def create_unidade(unidade: UnidadeCreate, db: Session = Depends(get_db)):
    try:
        db_unidade = Unidade(**unidade.model_dump())
        db.add(db_unidade)
        db.commit()
        db.refresh(db_unidade)
        return db_unidade
    except OperationalError as err:
        print("Erro de conexão com o banco de dados:", err)
        
        save_local_stage(partition_key="unidade",
                         action="create",
                         data=unidade.model_dump())
        raise HTTPException(status_code=503, detail="Erro de conexão com o banco de dados")
    except DatabaseError as err:
        print("Erro no servidor do banco de dados:", err)
        
        save_local_stage(partition_key="unidade",
                         action="create",
                         data=unidade.model_dump())

        raise HTTPException(status_code=500, detail="Erro no servidor do banco de dados")
    except Exception as err:
        print("Erro inesperado:", err)
        raise err
    
@router.get("/{id_unidade}", response_model=UnidadeResponse)
def get_unidade_by_id(id_unidade: int, db: Session = Depends(get_db)):
    unidade = db.query(Unidade).filter(Unidade.id_unidade == id_unidade).first()
    if not unidade:
        raise HTTPException(status_code=404, detail="Unidade não encontrada.")
    return unidade

@router.delete("/{id_unidade}")
def delete_unidade(id_unidade: int, db: Session = Depends(get_db)):
    unidade = db.query(Unidade).filter(Unidade.id_unidade == id_unidade).first()
    if not unidade:
        raise HTTPException(status_code=404, detail="Unidade não encontrada.")
    db.delete(unidade)
    db.commit()
    return {"message": "Unidade deletada com sucesso."}