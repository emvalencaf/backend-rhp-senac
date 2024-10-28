
#=======================================================================#CODIGO COMEÇA A PARTIR DE AGORA==================================#
# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models.models import Unidade # Importa o modelo Unidade do módulo models
from models.models import Paciente
from database import SessionLocal, engine, Base  # Importa a sessão e a engine do database.py
from pydantic import BaseModel

# Cria o aplicativo FastAPI
app = FastAPI()

#====== Rota Publica apenas para testar no Postman se esta tudo funcionando======
@app.get("/")
def root():
    return {"message": "API esta funcionando!"}

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Dependência que fornece uma sessão de banco de dados para cada requisição
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Esquema Pydantic para resposta
class UnidadeResponse(BaseModel):
    id_unidade: int
    nome_unidade: str

    class Config:
        orm_mode = True

# Esquema Pydantic para a criação de unidade
class UnidadeCreate(BaseModel):
    nome_unidade: str

# Esquema Pydantic para criação de paciente
class PacienteCreate(BaseModel):
    nome: str
    data_nascimento: str
    endereco: str
    cep: str
    nome_mae: str

    class Config:
        orm_mode = True

# Esquema Pydantic para resposta de paciente
class PacienteResponse(BaseModel):
    id_paciente: int
    nome: str
    data_nascimento: str
    endereco: str
    cep: str
    nome_mae: str

    class Config:
        orm_mode = True
        
# Rota GET para buscar todas as unidades hospitalares
@app.get("/unidade/", response_model=List[UnidadeResponse])
def get_unidades(db: Session = Depends(get_db)):
    unidades = db.query(Unidade).all()
    return unidades

# Rota POST para criar uma nova unidade
@app.post("/unidade/", response_model=UnidadeResponse)
def create_unidade(unidade: UnidadeCreate, db: Session = Depends(get_db)):
    new_unidade = Unidade(nome_unidade=unidade.nome_unidade)
    db.add(new_unidade)
    db.commit()
    db.refresh(new_unidade)
    return new_unidade

# Rota POST para criar os pacientes
@app.post("/pacientes/", response_model=PacienteResponse)
def create_paciente(paciente: PacienteCreate, db: Session = Depends(get_db)):
    db_paciente = paciente(**paciente.dict())
    db.add(db_paciente)
    db.commit()
    db.refresh(db_paciente)
    return db_paciente

# Rota GET para obter os pacientes
@app.get("/pacientes/", response_model=List[PacienteResponse])
def get_pacientes(db: Session = Depends(get_db)):
    pacientes = db.query(pacientes).all()
    return pacientes

# Rota PUT para atualizar as informaçoes dos pacientes
@app.put("/pacientes/{paciente_id}", response_model=PacienteResponse)
def update_paciente(paciente_id: int, updated_paciente: PacienteCreate, db: Session = Depends(get_db)):
    paciente = db.query(paciente).filter(paciente.id_paciente == paciente_id).first()
    if paciente is None:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    for key, value in updated_paciente.dict().items():
        setattr(paciente, key, value)

    db.commit()
    db.refresh(paciente)
    return paciente

#Rota DELETE para deletar paciente
@app.delete("/pacientes/{paciente_id}")
def delete_paciente(paciente_id: int, db: Session = Depends(get_db)):
    paciente = db.query(paciente).filter(paciente.id_paciente == paciente_id).first()
    if paciente is None:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    db.delete(paciente)
    db.commit()
    return {"detail": "Paciente deletado com sucesso"}