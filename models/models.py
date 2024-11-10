# models/models.py
from sqlalchemy import Column, Integer, String, Date, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from database import Base  # Importa a Base do database.py
from datetime import date

# Modelo para a tabela Unidade
class Unidade(Base):
    __tablename__ = 'unidade'
    
    id_unidade = Column(Integer, primary_key=True, autoincrement=True)
    nome_unidade = Column(String(255), nullable=False)
    descricao_unid = Column(String(255))
    
    # Relacionamento com a tabela Leito
    leitos = relationship("Leito", back_populates="unidade")

# Modelo para a tabela Leito
class Leito(Base):
    __tablename__ = 'leito'
    
    id_leito = Column(Integer, primary_key=True, autoincrement=True)
    id_unidade = Column(Integer, ForeignKey('unidade.id_unidade'), nullable=False)
    unidade_internacao = Column(String(255))
    
    # Relacionamento com as tabelas Unidade, Paciente, e Transferencia
    unidade = relationship("Unidade", back_populates="leitos")
    pacientes = relationship("Paciente", back_populates="leito")
    transferencias_origem = relationship("Transferencia", foreign_keys="[Transferencia.codigo_leito_origem]", back_populates="leito_origem")
    transferencias_destino = relationship("Transferencia", foreign_keys="[Transferencia.codigo_leito_destino]", back_populates="leito_destino")

# Modelo para a tabela Paciente
class Paciente(Base):
    __tablename__ = 'paciente'
    id_paciente = Column (Integer, primary_key=True, autoincrement=True)
    cpf = Column(String(11), nullable=False)
    nome = Column(String(255), nullable=False)
    data_nascimento = Column(Date)
    endereco = Column(String(255))
    cep = Column(String(20))
    nome_mae = Column(String(255))
    id_leito = Column(Integer, ForeignKey('leito.id_leito'))
    
    # Relacionamento com as tabelas Leito, Atendimento, Alta e Transferencia
    leito = relationship("Leito", back_populates="pacientes")
    atendimentos = relationship("Atendimento", back_populates="paciente")
    transferencias = relationship("Transferencia", back_populates="paciente")
    altas = relationship("Alta", back_populates="paciente")

# Modelo para a tabela Profissional
class Profissional(Base):
    __tablename__ = 'profissional'
    
    id_profissional = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(255))
    setor = Column(String(255))
    funcao = Column(String(255))
    
    # Relacionamento com a tabela Atendimento
    atendimentos = relationship("Atendimento", back_populates="profissional")

# Modelo para a tabela Atendimento
class Atendimento(Base):
    __tablename__ = 'atendimento'
    
    id_atendimento = Column(Integer, primary_key=True, autoincrement=True)
    data_hora = Column(TIMESTAMP)
    tipo = Column(String(100))
    origem = Column(String(100))
    convenio = Column(String(100))
    id_paciente = Column(String(11), ForeignKey('paciente.cpf'))
    id_profissional = Column(Integer, ForeignKey('profissional.id_profissional'))
    
    # Relacionamento com as tabelas Paciente e Profissional
    paciente = relationship("Paciente", back_populates="atendimentos")
    profissional = relationship("Profissional", back_populates="atendimentos")

# Modelo para a tabela Transferencia
class Transferencia(Base):
    __tablename__ = 'Transferencia'
    
    id_transferencia = Column(Integer, primary_key=True, autoincrement=True)
    cpf = Column(String(11), ForeignKey('paciente.cpf'))
    codigo_leito_origem = Column(Integer, ForeignKey('leito.id_leito'))
    codigo_leito_destino = Column(Integer, ForeignKey('leito.id_leito'))
    datahora_transferencia = Column(TIMESTAMP)
    
    # Relacionamento com as tabelas Paciente e Leito
    paciente = relationship("Paciente", back_populates="transferencias")
    leito_origem = relationship("Leito", foreign_keys=[codigo_leito_origem], back_populates="transferencias_origem")
    leito_destino = relationship("Leito", foreign_keys=[codigo_leito_destino], back_populates="transferencias_destino")

# Modelo Pydantic para a tabela Alta
class Alta(Base):
    __tablename__ = 'Alta'
    
    id_alta = Column(Integer, primary_key=True, autoincrement=True)
    data_hora_alta = Column(TIMESTAMP)
    motivo_alta = Column(String(255))
    cpf = Column(String(11), ForeignKey('paciente.cpf'))
    
    # Relacionamento com a tabela Paciente
    paciente = relationship("Paciente", back_populates="altas")
