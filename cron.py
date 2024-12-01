from os import getenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from contextlib import asynccontextmanager
from fastapi import FastAPI
import pandas as pd
import os
import json
from pathlib import Path
from sqlalchemy.exc import IntegrityError
from database import engine
from local_stage import ACTIONS, STAGING_AREA_PATH, IS_ABSOLUTE_STAGING_AREA_PATH, clean_local_stage
import logging

# Configuração do logging para rastrear operações
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CRONTAB = getenv('CRONTAB', '35 21 * * *')  # Isso significa 12:00 todos os dias

# Função para carregar dados em lotes e evitar uso excessivo de memória
def get_dataframe(action: str, partition_key: str):
    if action.lower() not in ACTIONS:
        raise ValueError(f"A ação deve ser uma das seguintes: {', '.join(ACTIONS)}")
    
    base_dir = Path(STAGING_AREA_PATH) if IS_ABSOLUTE_STAGING_AREA_PATH else Path.cwd() / STAGING_AREA_PATH
    dir_path = base_dir / action.lower() / partition_key
    
    if not dir_path.exists():
        return None
    
    json_files = []

    # Caminha pela estrutura de diretórios e pega os arquivos .json
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".json"):
                file_path = Path(root) / file
                relative_path = str(file_path).split(action)[1]
                
                parts = relative_path.split('\\')
                
                year = parts[-4]
                month = parts[-3]
                day = parts[-2]
                timestamp = parts[-1].split('.')[0]
                
                json_files.append((file_path, year, month, day, timestamp))
        
    json_files.sort(key=lambda x: (int(x[1]), int(x[2]), int(x[3]), int(x[4])))
    
    all_data = []
    
    # Processamento por lotes
    for file_path, year, month, day, timestamp in json_files:
        try:
            with open(file_path, 'r', encoding="utf-8") as f:
                data = json.load(f)
                all_data.append(data)
        except Exception as e:
            logger.error(f"Erro ao ler o arquivo {file_path}: {e}")

    if all_data:
        df = pd.DataFrame(all_data)
        logger.info(f"DataFrame carregado com {len(df)} registros.")
        return df
    else:
        logger.warning("Nenhum dado encontrado.")
        return None

def load_dataframe_to_sql(df: pd.DataFrame, table_name: str, action: str, partition_key: str):
    try:
        df = df.drop_duplicates()  # Remove dados duplicados

        if action == "update":
            col_id = f'id_{table_name}' if table_name not in ["paciente", "profissional"] else 'cpf'
            ids = tuple(df[col_id])

            if not ids:
                raise Exception("Não há IDs no DataFrame para realizar a atualização.")
            
            # Buscando os dados no banco para atualização
            query = f"SELECT * FROM {table_name} WHERE {col_id} IN {ids}"
            df_db = pd.read_sql(query, con=engine)

            for _, row in df.iterrows():
                matching_record = df_db[df_db[col_id] == row[col_id]]
                
                if not matching_record.empty:
                    update_values = ', '.join([f"{col} = '{row[col]}'" for col in df.columns if col != col_id])
                    update_query = f"UPDATE {table_name} SET {update_values} WHERE {col_id} = {row[col_id]}"
                    with engine.connect() as conn:
                        conn.execute(update_query)
                else:
                    row_data = ', '.join([f"'{row[col]}'" for col in df.columns])
                    insert_query = f"INSERT INTO {table_name} ({', '.join(df.columns)}) VALUES ({row_data})"
                    with engine.connect() as conn:
                        conn.execute(insert_query)
            
        else:
            df.to_sql(table_name, con=engine, if_exists='append', index=False)
        
        # Limpeza do estágio local após o processo
        clean_local_stage(action=action, partition_key=partition_key)
        logger.info(f"Dados {action} para {table_name} carregados com sucesso.")

    except IntegrityError as e:
        logger.error(f"Erro de integridade: {e}")
    except Exception as e:
        logger.error(f"Ocorreu um erro ao carregar dados: {e}")

# Função para carregar dados no banco de dados
def load_data():
    # Carrega dados de diferentes tabelas e partes do sistema
    try:
        # Carregando dados de várias tabelas para criar ou atualizar
        df_create_pacientes = get_dataframe(action="create", partition_key="paciente")
        df_update_pacientes = get_dataframe(action="update", partition_key="paciente")
        df_create_leito = get_dataframe(action="create", partition_key="leito")
        df_update_leito = get_dataframe(action="update", partition_key="leito")
        df_create_atendimento = get_dataframe(action="create", partition_key="atendimento")
        df_create_professional = get_dataframe(action="create", partition_key="professional")
        df_update_professional = get_dataframe(action="update", partition_key="professional")
        df_create_transferencia = get_dataframe(action="create", partition_key="transferencia")
        df_update_transferencia = get_dataframe(action="update", partition_key="transferencia")
        df_create_unidade = get_dataframe(action="create", partition_key="unidade")
        df_update_unidade = get_dataframe(action="update", partition_key="unidade")
        df_create_alta = get_dataframe(action="create", partition_key="alta")

        # Processa cada tipo de dado
        if df_create_pacientes is not None and not df_create_pacientes.empty:
            load_dataframe_to_sql(df_create_pacientes, table_name='paciente', action="create", partition_key="paciente")
        if df_update_pacientes is not None and not df_update_pacientes.empty:
            load_dataframe_to_sql(df_update_pacientes, table_name='paciente', action="update", partition_key="paciente")
        
        if df_create_leito is not None and not df_create_leito.empty:
            load_dataframe_to_sql(df_create_leito, table_name='leito', action="create", partition_key="leito")
        if df_update_leito is not None and not df_update_leito.empty:
            load_dataframe_to_sql(df_update_leito, table_name='leito', action="update", partition_key="leito")
        
        if df_create_atendimento is not None and not df_create_atendimento.empty:
            load_dataframe_to_sql(df_create_atendimento, table_name='atendimento', action="create", partition_key="atendimento")

        if df_create_professional is not None and not df_create_professional.empty:
            load_dataframe_to_sql(df_create_professional, table_name='profissional', action="create", partition_key="profissional")
        if df_update_professional is not None and not df_update_professional.empty:
            load_dataframe_to_sql(df_update_professional, table_name='profissional', action="update", partition_key="profissional")
        
        if df_create_transferencia is not None and not df_create_transferencia.empty:
            load_dataframe_to_sql(df_create_transferencia, table_name='transferencia', action="create", partition_key="transferencia")
        if df_update_transferencia is not None and not df_update_transferencia.empty:
            load_dataframe_to_sql(df_update_transferencia, table_name='transferencia', action="update", partition_key="transferencia")
        
        if df_update_unidade is not None and not df_update_unidade.empty:
            load_dataframe_to_sql(df_update_unidade, table_name='unidade', action="update", partition_key="unidade")

        if df_create_unidade is not None and not df_create_unidade.empty:
            load_dataframe_to_sql(df_create_unidade, table_name='unidade', action="create", partition_key="unidade")
        
        if df_create_alta is not None and not df_create_alta.empty:
            load_dataframe_to_sql(df_create_alta, table_name='alta', action="create", partition_key="alta")
               
        
    except Exception as e:
        logger.error(f"Erro ao carregar dados: {e}")

@asynccontextmanager
async def lifespan_scheduler(app: FastAPI):
    # Inicializa o agendador de tarefas
    scheduler = BackgroundScheduler()
    
    # Define o job usando a expressão cron
    scheduler.add_job(load_data, CronTrigger.from_crontab(CRONTAB))  # Usando o cron job configurado
    
    # Teste rápido com intervalo de 4 segundos
    # scheduler.add_job(load_data, 'interval', seconds=4)  # Para testes, use este intervalo

    scheduler.start()
    
    yield
    
    # Encerra o agendador ao finalizar a aplicação
    scheduler.shutdown()
