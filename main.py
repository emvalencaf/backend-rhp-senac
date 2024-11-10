# main.py
from fastapi import FastAPI, Depends, HTTPException
from datetime import date
from sqlalchemy.orm import Session, joinedload
from typing import List
from models.models import Unidade, Paciente, Leito, Transferencia, Alta, Atendimento, Profissional # Importa os models
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

# Esquema Pydantic para ver todas as unidades
class UnidadeResponse(BaseModel):
    id_unidade: int
    nome_unidade: str

    class Config:
        orm_mode = True

# Esquema Pydantic para a criação de unidade
class UnidadeCreate(BaseModel):
    nome_unidade: str

#Atualizar informaçoes da unidade hospitalar
from typing import Optional
class UnidadeUpdate(BaseModel):
    nome_unidade: Optional[str]

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

#Rota PUT para atualizar as informaçoes das unidades hospitalares buscando elas pelos ID, preferi do que
@app.get("/unidades/{id_unidade}", response_model=UnidadeResponse)
def get_unidade_by_id(id_unidade: int, db: Session = Depends(get_db)):
    unidade = db.query(Unidade).filter(Unidade.id_unidade == id_unidade).first()
    # Verifica se a unidade existe
    if unidade is None:
        raise HTTPException(status_code=404, detail="Unidade não encontrada")
    return unidade

# Rota DELETE para deletar uma unidade pelo ID
@app.delete("/unidades/{id_unidade}", response_model=UnidadeResponse)
def delete_unidade(id_unidade: int, db: Session = Depends(get_db)):
    # Busca a unidade pelo ID no banco de dados
    unidade = db.query(Unidade).filter(Unidade.id_unidade == id_unidade).first()
    # Verifica se a unidade existe
    if unidade is None:
        raise HTTPException(status_code=404, detail="Unidade não encontrada")
    # Deleta a unidade encontada
    db.delete(unidade)
    db.commit()

    return unidade

# Esquema Pydantic para criação de paciente
class PacienteCreate(BaseModel):
    cpf: str
    nome: str
    data_nascimento: date
    endereco: str
    cep: str
    nome_mae: str
    id_leito: int

    class Config:
        orm_mode = True

# Esquema Pydantic para aparecer todos os pacientes registrados emodificar a dat de nascimento para date
class PacienteResponse(BaseModel):
    cpf: str
    nome: str
    data_nascimento: date
    endereco: str
    cep: str
    nome_mae: str
    id_leito: int

    class Config:
        orm_mode = True

# Esquema Pydantic para atualização de paciente
class PacienteUpdate(BaseModel):
    cpf:str
    nome: str
    data_nascimento: date
    endereco: str
    cep: str
    nome_mae: str
    id_leito: int

    class Config:
        orm_mode = True

# Rota POST para criar os pacientes
@app.post("/paciente/", response_model=PacienteResponse)
def create_paciente(paciente: PacienteCreate, db: Session = Depends(get_db)):
    db_paciente = Paciente(
        cpf=paciente.cpf,
        nome=paciente.nome,
        data_nascimento=paciente.data_nascimento,
        endereco=paciente.endereco,
        cep=paciente.cep,
        nome_mae=paciente.nome_mae,
        id_leito=paciente.id_leito
    )
    db.add(db_paciente)
    db.commit()
    db.refresh(db_paciente)
    return db_paciente

# Rota GET para obter os pacientes
@app.get("/paciente/", response_model=List[PacienteResponse])
def get_paciente(db: Session = Depends(get_db)):
    pacientes = db.query(Paciente).all()
    return pacientes

# Rota PUT para atualizar as informaçoes dos pacientes
@app.put("/paciente/{cpf}", response_model=PacienteResponse)
def update_paciente(cpf:str, paciente_update: PacienteUpdate, db: Session = Depends(get_db)):
    # Busca o paciente pelo ID
    paciente = db.query(Paciente).filter(paciente.cpf == cpf).first()

    # Verifica se o paciente existe
    if paciente is None:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    # Atualiza as informações do paciente
    paciente.cpf = paciente_update.cpf
    paciente.nome = paciente_update.nome
    paciente.data_nascimento = paciente_update.data_nascimento
    paciente.endereco = paciente_update.endereco
    paciente.cep = paciente_update.cep
    paciente.nome_mae = paciente_update.nome_mae

    db.commit()
    db.refresh(paciente)
    return paciente

#Rota DELETE para deletar paciente
@app.delete("/paciente/{cpf}")
def delete_paciente(cpf: str, db: Session = Depends(get_db)):
    # Busca o paciente pelo ID no banco de dados
    paciente = db.query(Paciente).filter(Paciente.cpf == cpf).first()

    # Verifica se o paciente existe
    if paciente is None:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    # Deleta o paciente encontrado
    db.delete(paciente)
    db.commit()
    return paciente

# Esquema Pydantic para criar um leito
class LeitoCreate(BaseModel):
    id_unidade: int  # ID da unidade já existente criado no BD
    unidade_internacao: str

    class Config:
        orm_mode = True

# Esquema Pydantic para resposta dos leitos qque foram criados
class LeitoResponse(BaseModel):
    id_leito: int
    id_unidade: int
    unidade_internacao: str

    class Config:
        orm_mode = True

# Rota POST para criar um leito
@app.post("/leito/", response_model=LeitoResponse)
def create_leito(leito: LeitoCreate, db: Session = Depends(get_db)):
    # Verifica se a unidade existe
    unidade = db.query(Unidade).filter(Unidade.id_unidade == leito.id_unidade).first()
    if unidade is None:
        raise HTTPException(status_code=404, detail="Unidade não encontrada")
    
    new_leito = Leito(
        id_unidade=leito.id_unidade,
        unidade_internacao=leito.unidade_internacao
    )
    db.add(new_leito)
    db.commit()
    db.refresh(new_leito)
    return new_leito

# Rota GET para buscar todos os leitos
@app.get("/leito/", response_model=List[LeitoResponse])
def get_leitos(db: Session = Depends(get_db)):
    leitos = db.query(Leito).all()
    return leitos

# Rota PUT para atualizar um leito
@app.put("/leito/{id_leito}", response_model=LeitoResponse)
def update_leito(id_leito: int, leito: LeitoCreate, db: Session = Depends(get_db)):
    leito_db = db.query(Leito).filter(Leito.id_leito == id_leito).first()
    if leito_db is None:
        raise HTTPException(status_code=404, detail="Leito não encontrado")
    
    leito_db.id_unidade = leito.id_unidade
    leito_db.unidade_internacao = leito.unidade_internacao
    db.commit()
    db.refresh(leito_db)
    return leito_db

# Rota DELETE para deletar um leito chamando o ID dele
@app.delete("/leito/{id_leito}", response_model=LeitoResponse)
def delete_leito(id_leito: int, db: Session = Depends(get_db)):
    leito = db.query(Leito).filter(Leito.id_leito == id_leito).first()
    if leito is None:
        raise HTTPException(status_code=404, detail="Leito não encontrado")
    
    db.delete(leito)
    db.commit()
    return leito

# Esquema Pydantic para criação de transferência
class TransferenciaCreate(BaseModel):
    cpf: str
    codigo_leito_origem: int
    codigo_leito_destino: int
    datahora_transferencia: date

    class Config:
        orm_mode = True

# Esquema Pydantic para resposta da transferência
class TransferenciaResponse(BaseModel):
    id_transferencia: int
    cpf: str
    codigo_leito_origem: int
    codigo_leito_destino: int
    datahora_transferencia: date

    class Config:
        orm_mode = True
@app.get("/transferencia/", response_model=List[TransferenciaResponse])
def get_transferencias(db: Session = Depends(get_db)):
    transferencias = db.query(Transferencia).all()
    return transferencias

@app.post("/Transferencia/", response_model=TransferenciaResponse)
def create_transferencia(transferencia: TransferenciaCreate, db: Session = Depends(get_db)):
    # Verifica se o paciente existe
    paciente = db.query(Paciente).filter(Paciente.cpf == transferencia.cpf).first()
    if paciente is None:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    # Verifica se os leitos de origem e destino existem
    leito_origem = db.query(Leito).filter(Leito.id_leito == transferencia.codigo_leito_origem).first()
    leito_destino = db.query(Leito).filter(Leito.id_leito == transferencia.codigo_leito_destino).first()
    if leito_origem is None or leito_destino is None:
        raise HTTPException(status_code=404, detail="Leito de origem ou destino não encontrado")

    # Cria a nova transferência
    new_transferencia = Transferencia(
        cpf=transferencia.cpf,
        codigo_leito_origem=transferencia.codigo_leito_origem,
        codigo_leito_destino=transferencia.codigo_leito_destino,
        datahora_transferencia=transferencia.datahora_transferencia
    )
    db.add(new_transferencia)
    db.commit()
    db.refresh(new_transferencia)
    return new_transferencia

@app.put("/transferencia/{id_transferencia}", response_model=TransferenciaResponse)
def update_transferencia(id_transferencia: int, transferencia_update: TransferenciaCreate, db: Session = Depends(get_db)):
    # Busca a transferência existente pelo ID
    transferencia = db.query(Transferencia).filter(Transferencia.id_transferencia == id_transferencia).first()
    if transferencia is None:
        raise HTTPException(status_code=404, detail="Transferência não encontrada")

    # Atualiza os campos
    transferencia.cpf = transferencia_update.cpf
    transferencia.codigo_leito_origem = transferencia_update.codigo_leito_origem
    transferencia.codigo_leito_destino = transferencia_update.codigo_leito_destino
    transferencia.datahora_transferencia = transferencia_update.datahora_transferencia

    db.commit()
    db.refresh(transferencia)
    return transferencia

@app.delete("/transferencia/{id_transferencia}", response_model=TransferenciaResponse)
def delete_transferencia(id_transferencia: int, db: Session = Depends(get_db)):
    transferencia = db.query(Transferencia).filter(Transferencia.id_transferencia == id_transferencia).first()
    if transferencia is None:
        raise HTTPException(status_code=404, detail="Transferência não encontrada")
    
    db.delete(transferencia)
    db.commit()
    return transferencia

# Modelo Pydantic para criação de uma nova Alta
class AltaCreate(BaseModel):
    data_hora_alta: date
    motivo_alta: str
    cpf: str  # CPF do paciente

    class Config:
        orm_mode = True

# Modelo Pydantic para exibir as Altas registradas
class AltaResponse(BaseModel):
    id_alta: int
    data_hora_alta: date
    motivo_alta: str
    cpf: str  # CPF do paciente

    class Config:
        orm_mode = True

# Modelo Pydantic para atualizar uma Alta
class AltaUpdate(BaseModel):
    data_hora_alta: Optional[date] = None
    motivo_alta: Optional[str] = None
    cpf: Optional[str] = None

    class Config:
        orm_mode = True
        
# Esquema Pydantic para exibir as Altas com os dados do paciente associado
class AltaResponse(BaseModel):
    id_alta: int
    data_hora_alta: date
    motivo_alta: str
    cpf: str
    paciente: Optional[PacienteResponse]  # Incluindo o paciente no retorno

    class Config:
        orm_mode = True
        
# Rota POST para criar uma nova Alta
@app.post("/alta/", response_model=AltaResponse)
def create_alta(alta: AltaCreate, db: Session = Depends(get_db)):
    db_alta = Alta(
        data_hora_alta=alta.data_hora_alta,
        motivo_alta=alta.motivo_alta,
        cpf=alta.cpf
    )
    db.add(db_alta)
    db.commit()
    db.refresh(db_alta)
    return db_alta

# Rota GET para listar todas as Altas
@app.get("/alta/", response_model=List[AltaResponse])
def get_altas(db: Session = Depends(get_db)):
    altas = db.query(Alta).all()
    return altas

# Rota GET para obter uma Alta específica com dados do paciente associado
@app.get("/alta/{cpf}", response_model=AltaResponse)
def get_alta(cpf: str, db: Session = Depends(get_db)):
    alta = db.query(Alta).options(joinedload(Alta.paciente)).filter(Alta.cpf == cpf).first()
    if alta is None:
        raise HTTPException(status_code=404, detail="Alta não encontrada")
    return alta

# Rota DELETE para remover Altas pelo CPF do paciente
@app.delete("/alta/paciente/{cpf}", response_model=List[AltaResponse])
def delete_altas_by_cpf(cpf: str, db: Session = Depends(get_db)):
    # Busca todas as altas relacionadas ao CPF
    altas = db.query(Alta).filter(Alta.cpf == cpf).all()

    # Verifica se existe alguma alta associada ao CPF
    if not altas:
        raise HTTPException(status_code=404, detail="Nenhuma alta encontrada para este CPF")

    # Remove cada alta encontrada
    for alta in altas:
        db.delete(alta)
    # Confirma a transação
    db.commit()
    return altas

# Esquema Pydantic para criar um Profissional
class ProfissionalCreate(BaseModel):
    nome: str
    setor: str
    funcao: str

    class Config:
        orm_mode = True

# Esquema Pydantic para resposta de Profissional
class ProfissionalResponse(BaseModel):
    id_profissional: int
    nome: str
    setor: str
    funcao: str

    class Config:
        orm_mode = True

# Rota POST para criar um novo profissional
@app.post("/profissional/", response_model=ProfissionalResponse)
def create_profissional(profissional: ProfissionalCreate, db: Session = Depends(get_db)):
    new_profissional = Profissional(
        nome=profissional.nome,
        setor=profissional.setor,
        funcao=profissional.funcao
    )
    db.add(new_profissional)
    db.commit()
    db.refresh(new_profissional)
    return new_profissional

# Rota GET para buscar todos os profissionais
@app.get("/profissional/", response_model=List[ProfissionalResponse])
def get_profissionais(db: Session = Depends(get_db)):
    profissionais = db.query(Profissional).all()
    return profissionais

# Rota GET para buscar um profissional pelo ID
@app.get("/profissional/{id_profissional}", response_model=ProfissionalResponse)
def get_profissional_by_id(id_profissional: int, db: Session = Depends(get_db)):
    profissional = db.query(Profissional).filter(Profissional.id_profissional == id_profissional).first()
    if profissional is None:
        raise HTTPException(status_code=404, detail="Profissional não encontrado")
    return profissional

# Rota PUT para atualizar um profissional
@app.put("/profissional/{id_profissional}", response_model=ProfissionalResponse)
def update_profissional(id_profissional: int, profissional_data: ProfissionalCreate, db: Session = Depends(get_db)):
    profissional = db.query(Profissional).filter(Profissional.id_profissional == id_profissional).first()
    if profissional is None:
        raise HTTPException(status_code=404, detail="Profissional não encontrado")

    profissional.nome = profissional_data.nome
    profissional.setor = profissional_data.setor
    profissional.funcao = profissional_data.funcao

    db.commit()
    db.refresh(profissional)
    return profissional

# Rota DELETE para deletar um profissional
@app.delete("/profissional/{id_profissional}", response_model=ProfissionalResponse)
def delete_profissional(id_profissional: int, db: Session = Depends(get_db)):
    profissional = db.query(Profissional).filter(Profissional.id_profissional == id_profissional).first()
    if profissional is None:
        raise HTTPException(status_code=404, detail="Profissional não encontrado")

    db.delete(profissional)
    db.commit()
    return profissional

# Esquema Pydantic para criar um Atendimento
class AtendimentoCreate(BaseModel):
    data_hora: date
    tipo: str
    origem: str
    convenio: str
    id_paciente: int
    id_profissional: int

    class Config:
        orm_mode = True

# Esquema Pydantic para resposta de Atendimento
class AtendimentoResponse(BaseModel):
    id_atendimento: int
    data_hora: date
    tipo: str
    origem: str
    convenio: str
    id_paciente: int
    id_profissional: int

    class Config:
        orm_mode = True

# Rota POST para criar um novo atendimento
@app.post("/atendimento/", response_model=AtendimentoResponse)
def create_atendimento(atendimento: AtendimentoCreate, db: Session = Depends(get_db)):
    new_atendimento = Atendimento(
        data_hora=atendimento.data_hora,
        tipo=atendimento.tipo,
        origem=atendimento.origem,
        convenio=atendimento.convenio,
        id_paciente=atendimento.id_paciente,
        id_profissional=atendimento.id_profissional
    )
    db.add(new_atendimento)
    db.commit()
    db.refresh(new_atendimento)
    return new_atendimento

# Rota GET para buscar todos os atendimentos
@app.get("/atendimento/", response_model=List[AtendimentoResponse])
def get_atendimentos(db: Session = Depends(get_db)):
    atendimentos = db.query(Atendimento).all()
    return atendimentos

# Rota GET para buscar um atendimento pelo ID
@app.get("/atendimento/{id_atendimento}", response_model=AtendimentoResponse)
def get_atendimento_by_id(id_atendimento: int, db: Session = Depends(get_db)):
    atendimento = db.query(Atendimento).filter(Atendimento.id_atendimento == id_atendimento).first()
    if atendimento is None:
        raise HTTPException(status_code=404, detail="Atendimento não encontrado")
    return atendimento

# Rota PUT para atualizar um atendimento
@app.put("/atendimento/{id_atendimento}", response_model=AtendimentoResponse)
def update_atendimento(id_atendimento: int, atendimento_data: AtendimentoCreate, db: Session = Depends(get_db)):
    atendimento = db.query(Atendimento).filter(Atendimento.id_atendimento == id_atendimento).first()
    if atendimento is None:
        raise HTTPException(status_code=404, detail="Atendimento não encontrado")

    atendimento.data_hora = atendimento_data.data_hora
    atendimento.tipo = atendimento_data.tipo
    atendimento.origem = atendimento_data.origem
    atendimento.convenio = atendimento_data.convenio
    atendimento.id_paciente = atendimento_data.id_paciente
    atendimento.id_profissional = atendimento_data.id_profissional

    db.commit()
    db.refresh(atendimento)
    return atendimento

# Rota DELETE para deletar um atendimento
@app.delete("/atendimento/{id_atendimento}", response_model=AtendimentoResponse)
def delete_atendimento(id_atendimento: int, db: Session = Depends(get_db)):
    atendimento = db.query(Atendimento).filter(Atendimento.id_atendimento == id_atendimento).first()
    if atendimento is None:
        raise HTTPException(status_code=404, detail="Atendimento não encontrado")

    db.delete(atendimento)
    db.commit()
    return atendimento
