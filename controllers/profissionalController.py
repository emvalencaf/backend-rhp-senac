from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from models.models import Profissional
from database import SessionLocal, engine, Base
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/profissional", tags=["Profissional"])

# Cria as tabelas no banco de dados (garantia adicional, mas não essencial em produção)
Base.metadata.create_all(bind=engine)

# Dependência para fornecer uma sessão de banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Esquema Pydantic para resposta com profissional
class ProfissionalResponse(BaseModel):
    cpf: str
    nome: str
    setor: Optional[str] = None
    funcao: Optional[str] = None

    class Config:
        orm_mode = True  # Permite retornar objetos do SQLAlchemy diretamente

# Esquema Pydantic para criação de profissional
class ProfissionalCreate(BaseModel):
    cpf: str
    nome: str
    setor: Optional[str] = None
    funcao: Optional[str] = None

# Esquema Pydantic para atualização parcial de profissional
class ProfissionalUpdate(BaseModel):
    nome: Optional[str] = None
    setor: Optional[str] = None
    funcao: Optional[str] = None

    class Config:
        orm_mode = True

# Endpoints

@router.get("/", response_model=List[ProfissionalResponse])
def get_profissionais(db: Session = Depends(get_db)):
    """Retorna todos os profissionais cadastrados."""
    profissionais = db.query(Profissional).all()
    return profissionais

@router.post("/", response_model=ProfissionalResponse, status_code=status.HTTP_201_CREATED)
def create_profissional(profissional: ProfissionalCreate, db: Session = Depends(get_db)):
    """Cria um novo profissional."""
    if db.query(Profissional).filter(Profissional.cpf == profissional.cpf).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="CPF já cadastrado."
        )
    db_profissional = Profissional(**profissional.dict())
    db.add(db_profissional)
    db.commit()
    db.refresh(db_profissional)
    return db_profissional

@router.get("/{cpf}", response_model=ProfissionalResponse)
def get_profissional_by_cpf(cpf: str, db: Session = Depends(get_db)):
    """Retorna um profissional pelo CPF."""
    profissional = db.query(Profissional).filter(Profissional.cpf == cpf).first()
    if not profissional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profissional não encontrado."
        )
    return profissional

@router.put("/{cpf}", response_model=ProfissionalResponse)
def update_profissional(
    cpf: str, profissional_update: ProfissionalUpdate, db: Session = Depends(get_db)
):
    """Atualiza um profissional pelo CPF."""
    profissional = db.query(Profissional).filter(Profissional.cpf == cpf).first()
    if not profissional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profissional não encontrado."
        )
    for field, value in profissional_update.dict(exclude_unset=True).items():
        setattr(profissional, field, value)
    db.commit()
    db.refresh(profissional)
    return profissional

@router.delete("/{cpf}", status_code=status.HTTP_200_OK)
def delete_profissional(cpf: str, db: Session = Depends(get_db)):
    """Deleta um profissional pelo CPF e retorna o nome do profissional deletado."""
    profissional = db.query(Profissional).filter(Profissional.cpf == cpf).first()
    if not profissional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profissional não encontrado."
        )
    
    nome_profissional = profissional.nome  # Armazena o nome antes de deletar
    db.delete(profissional)
    db.commit()
    
    return {
        "message": "Profissional deletado com sucesso.",
        "nome": nome_profissional
    }

