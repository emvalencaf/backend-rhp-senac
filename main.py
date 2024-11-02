from datetime import datetime
from typing import List
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

app = FastAPI()

# Configuração do banco de dados
DATABASE_URL = "sqlite:///./hospital.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelos do banco de dados
class UnidadeHospitalar(Base):
    __tablename__ = "unidades_hospitalares"
    id_unidade = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    localizacao = Column(String)

class Paciente(Base):
    __tablename__ = "pacientes"
    id_paciente = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    idade = Column(Integer)
    genero = Column(String)

class Leito(Base):
    __tablename__ = "leitos"
    id_leito = Column(Integer, primary_key=True, index=True)
    tipo = Column(String)
    ocupado = Column(Integer)

class Profissional(Base):
    __tablename__ = "profissionais"
    id_profissional = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    setor = Column(String)
    funcao = Column(String)

class Atendimento(Base):
    __tablename__ = "atendimentos"
    id_atendimento = Column(Integer, primary_key=True, index=True)
    data_hora = Column(DateTime)
    tipo = Column(String)
    origem = Column(String)
    convenio = Column(String)
    id_paciente = Column(Integer)
    id_profissional = Column(Integer)

Base.metadata.create_all(bind=engine)

# Dependência do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Schemas Pydantic
class UnidadeHospitalarCreate(BaseModel):
    nome: str
    localizacao: str

class UnidadeHospitalarResponse(UnidadeHospitalarCreate):
    id_unidade: int

class PacienteCreate(BaseModel):
    nome: str
    idade: int
    genero: str

class PacienteResponse(PacienteCreate):
    id_paciente: int

class LeitoCreate(BaseModel):
    tipo: str
    ocupado: int

class LeitoResponse(LeitoCreate):
    id_leito: int

class ProfissionalCreate(BaseModel):
    nome: str
    setor: str
    funcao: str

class ProfissionalResponse(ProfissionalCreate):
    id_profissional: int

class AtendimentoCreate(BaseModel):
    data_hora: datetime
    tipo: str
    origem: str
    convenio: str
    id_paciente: int
    id_profissional: int

class AtendimentoResponse(AtendimentoCreate):
    id_atendimento: int

# Rotas CRUD para Unidade Hospitalar
@app.post("/unidade/", response_model=UnidadeHospitalarResponse)
def create_unidade(unidade: UnidadeHospitalarCreate, db: Session = Depends(get_db)):
    new_unidade = UnidadeHospitalar(**unidade.dict())
    db.add(new_unidade)
    db.commit()
    db.refresh(new_unidade)
    return new_unidade

@app.get("/unidade/", response_model=List[UnidadeHospitalarResponse])
def get_unidades(db: Session = Depends(get_db)):
    return db.query(UnidadeHospitalar).all()

@app.put("/unidade/{id_unidade}", response_model=UnidadeHospitalarResponse)
def update_unidade(id_unidade: int, unidade_update: UnidadeHospitalarCreate, db: Session = Depends(get_db)):
    unidade = db.query(UnidadeHospitalar).filter(UnidadeHospitalar.id_unidade == id_unidade).first()
    if unidade is None:
        raise HTTPException(status_code=404, detail="Unidade não encontrada")
    for key, value in unidade_update.dict().items():
        setattr(unidade, key, value)
    db.commit()
    db.refresh(unidade)
    return unidade

@app.delete("/unidade/{id_unidade}", response_model=UnidadeHospitalarResponse)
def delete_unidade(id_unidade: int, db: Session = Depends(get_db)):
    unidade = db.query(UnidadeHospitalar).filter(UnidadeHospitalar.id_unidade == id_unidade).first()
    if unidade is None:
        raise HTTPException(status_code=404, detail="Unidade não encontrada")
    db.delete(unidade)
    db.commit()
    return unidade

# Rotas CRUD para Paciente
@app.post("/paciente/", response_model=PacienteResponse)
def create_paciente(paciente: PacienteCreate, db: Session = Depends(get_db)):
    new_paciente = Paciente(**paciente.dict())
    db.add(new_paciente)
    db.commit()
    db.refresh(new_paciente)
    return new_paciente

@app.get("/paciente/", response_model=List[PacienteResponse])
def get_pacientes(db: Session = Depends(get_db)):
    return db.query(Paciente).all()

@app.put("/paciente/{id_paciente}", response_model=PacienteResponse)
def update_paciente(id_paciente: int, paciente_update: PacienteCreate, db: Session = Depends(get_db)):
    paciente = db.query(Paciente).filter(Paciente.id_paciente == id_paciente).first()
    if paciente is None:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    for key, value in paciente_update.dict().items():
        setattr(paciente, key, value)
    db.commit()
    db.refresh(paciente)
    return paciente

@app.delete("/paciente/{id_paciente}", response_model=PacienteResponse)
def delete_paciente(id_paciente: int, db: Session = Depends(get_db)):
    paciente = db.query(Paciente).filter(Paciente.id_paciente == id_paciente).first()
    if paciente is None:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    db.delete(paciente)
    db.commit()
    return paciente

# Rotas CRUD para Leito
@app.post("/leito/", response_model=LeitoResponse)
def create_leito(leito: LeitoCreate, db: Session = Depends(get_db)):
    new_leito = Leito(**leito.dict())
    db.add(new_leito)
    db.commit()
    db.refresh(new_leito)
    return new_leito

@app.get("/leito/", response_model=List[LeitoResponse])
def get_leitos(db: Session = Depends(get_db)):
    return db.query(Leito).all()

@app.put("/leito/{id_leito}", response_model=LeitoResponse)
def update_leito(id_leito: int, leito_update: LeitoCreate, db: Session = Depends(get_db)):
    leito = db.query(Leito).filter(Leito.id_leito == id_leito).first()
    if leito is None:
        raise HTTPException(status_code=404, detail="Leito não encontrado")
    for key, value in leito_update.dict().items():
        setattr(leito, key, value)
    db.commit()
    db.refresh(leito)
    return leito

@app.delete("/leito/{id_leito}", response_model=LeitoResponse)
def delete_leito(id_leito: int, db: Session = Depends(get_db)):
    leito = db.query(Leito).filter(Leito.id_leito == id_leito).first()
    if leito is None:
        raise HTTPException(status_code=404, detail="Leito não encontrado")
    db.delete(leito)
    db.commit()
    return leito

# Rotas CRUD para Profissional
@app.post("/profissional/", response_model=ProfissionalResponse)
def create_profissional(profissional: ProfissionalCreate, db: Session = Depends(get_db)):
    new_profissional = Profissional(**profissional.dict())
    db.add(new_profissional)
    db.commit()
    db.refresh(new_profissional)
    return new_profissional

@app.get("/profissional/", response_model=List[ProfissionalResponse])
def get_profissionais(db: Session = Depends(get_db)):
    return db.query(Profissional).all()

@app.put("/profissional/{id_profissional}", response_model=ProfissionalResponse)
def update_profissional(id_profissional: int, profissional_update: ProfissionalCreate, db: Session = Depends(get_db)):
    profissional = db.query(Profissional).filter(Profissional.id_profissional == id_profissional).first()
    if profissional is None:
        raise HTTPException(status_code=404, detail="Profissional não encontrado")
    for key, value in profissional_update.dict().items():
        setattr(profissional, key, value)
    db.commit()
    db.refresh(profissional)
    return profissional

@app.delete("/profissional/{id_profissional}", response_model=ProfissionalResponse)
def delete_profissional(id_profissional: int, db: Session = Depends(get_db)):
    profissional = db.query(Profissional).filter(Profissional.id_profissional == id_profissional).first()
    if profissional is None:
        raise HTTPException(status_code=404, detail="Profissional não encontrado")
    db.delete(profissional)
    db.commit()
    return profissional

# Rotas CRUD para Atendimento
@app.post("/atendimento/", response_model=AtendimentoResponse)
def create_atendimento(atendimento: AtendimentoCreate, db: Session = Depends(get_db)):
    new_atendimento = Atendimento(**atendimento.dict())
    db.add(new_atendimento)
    db.commit()
    db.refresh(new_atendimento)
    return new_atendimento

@app.get("/atendimento/", response_model=List[AtendimentoResponse])
def get_atendimentos(db: Session = Depends(get_db)):
    return db.query(Atendimento).all()

@app.put("/atendimento/{id_atendimento}", response_model=AtendimentoResponse)
def update_atendimento(id_atendimento: int, atendimento_update: AtendimentoCreate, db: Session = Depends(get_db)):
    atendimento = db.query(Atendimento).filter(Atendimento.id_atendimento == id_atendimento).first()
    if atendimento is None:
        raise HTTPException(status_code=404, detail="Atendimento não encontrado")
    for key, value in atendimento_update.dict().items():
        setattr(atendimento, key, value)
    db.commit()
    db.refresh(atendimento)
    return atendimento

@app.delete("/atendimento/{id_atendimento}", response_model=AtendimentoResponse)
def delete_atendimento(id_atendimento: int, db: Session = Depends(get_db)):
    atendimento = db.query(Atendimento).filter(Atendimento.id_atendimento == id_atendimento).first()
    if atendimento is None:
        raise HTTPException(status_code=404, detail="Atendimento não encontrado")
    db.delete(atendimento)
    db.commit()
    return atendimento
