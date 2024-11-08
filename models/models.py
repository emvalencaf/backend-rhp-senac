# models/models.py
from sqlalchemy import Column, Integer, String, Date, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from database import Base  # Importa a Base do database.py
from datetime import datetime

# Modelo para a tabela Unidade
class Unidade(Base):
    __tablename__ = 'unidade'
    
    id_unidade = Column(Integer, primary_key=True, autoincrement=True)
    nome_unidade = Column(String(255), nullable=False)
    
    # Relacionamento com a tabela Leito
    leitos = relationship("Leito", back_populates="unidade")

# Modelo para a tabela Leito
class Leito(Base):
    __tablename__ = 'leito'
    
    id_leito = Column(Integer, primary_key=True, autoincrement=True)
    id_unidade = Column(Integer, ForeignKey('unidade.id_unidade'), nullable=False)
    unidade_internacao = Column(String(255))
    
    # Relacionamento com as tabelas Unidade e Paciente
    unidade = relationship("Unidade", back_populates="leitos")
    pacientes = relationship("Paciente", back_populates="leito")

# Modelo para a tabela Paciente
class Paciente(Base):
    __tablename__ = 'paciente'
    
    id_paciente = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    data_nascimento = Column(Date)
    endereco = Column(String(255))
    cep = Column(String(20))
    nome_mae = Column(String(255))
    id_leito = Column(Integer, ForeignKey('leito.id_leito'))
    
    # Relacionamento com as tabelas Leito e Atendimento
    leito = relationship("Leito", back_populates="pacientes")
    atendimentos = relationship("Atendimento", back_populates="paciente")

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
    id_paciente = Column(Integer, ForeignKey('paciente.id_paciente'))
    id_profissional = Column(Integer, ForeignKey('profissional.id_profissional'))
    
    # Relacionamento com as tabelas Paciente e Profissional
    paciente = relationship("Paciente", back_populates="atendimentos")
    profissional = relationship("Profissional", back_populates="atendimentos")
