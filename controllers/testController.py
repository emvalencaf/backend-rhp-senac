from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from database import SessionLocal, engine, Base
from models.models import Unidade, Paciente, Leito, Transferencia, Alta, Atendimento, Profissional

router = APIRouter(prefix="/test", tags=["Test"])

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Dependência que fornece uma sessão de banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rota para testar se a API está ativa
@router.get("/")
def test_api():
    return {"message": "API está funcionando!"}

# Rota para verificar o status do banco de dados
@router.get("/db-status")
def check_db_status(db: Session = Depends(get_db)):
    try:
        # Tenta realizar uma consulta simples para verificar a conexão
        db.execute(text("SELECT 1"))
        return {"message": "Conexão com o banco de dados bem-sucedida."}
    except Exception as e:
        return {"error": f"Erro ao conectar ao banco de dados: {str(e)}"}

# Rota para listar contagens de registros nas tabelas principais
@router.get("/table-counts")
def get_table_counts(db: Session = Depends(get_db)):
    try:
        counts = {
            "unidades": db.query(Unidade).count(),
            "pacientes": db.query(Paciente).count(),
            "leitos": db.query(Leito).count(),
            "transferencias": db.query(Transferencia).count(),
            "altas": db.query(Alta).count(),
            "atendimentos": db.query(Atendimento).count(),
            "profissionais": db.query(Profissional).count(),
        }
        return {"table_counts": counts}
    except Exception as e:
        return {"error": f"Erro ao obter contagem de registros: {str(e)}"}