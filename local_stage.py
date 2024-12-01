import json
from datetime import datetime
from os import getenv, makedirs
from pathlib import Path
from dotenv import load_dotenv
import shutil


load_dotenv()

# endereço do particionamento <staging_area_path>/<actions>/<partition_key>/<year>/<month>/<day>
STAGING_AREA_PATH = getenv('STAGING_AREA_PATH', 'data/')  # Local do Staging
IS_ABSOLUTE_STAGING_AREA_PATH = getenv('IS_ABSOLUTE_STAGING_AREA_PATH', "False").strip().lower() == "true"

ACTIONS = ("create", "update")

def save_local_stage(partition_key: str,
                     action: str,
                     data: dict):
    if (action.lower() not in ACTIONS):
        raise Exception("A ação deve estar listada nas ações")
    
    # Define o diretório base para o staging, convertendo para absoluto se necessário
    base_dir = Path(STAGING_AREA_PATH) if IS_ABSOLUTE_STAGING_AREA_PATH else Path.cwd() / STAGING_AREA_PATH
    
    dir_name = base_dir / action / partition_key
    
    # Cria o diretório, caso não exista
    makedirs(dir_name,
             exist_ok=True)
    
    # Obtém a data e hora atuais para estrutura de diretório e nome do arquivo
    now = datetime.now()
    dir_datetime = f'{now.year}/{now.month:02}/{now.day:02}'
    
    # Gera o nome do arquivo com timestamp para garantir unicidade
    timestamp = int(now.timestamp())
    full_path = dir_name / dir_datetime / f"{timestamp}.json"
    
    # Garante que todos os diretórios necessários existam
    makedirs(full_path.parent, exist_ok=True)
    
    # Salva os dados como JSON com tratamento de erro
    try:
        with open(full_path, "w", encoding='ISO-8859-1') as f:
            json.dump(data, f, default=str)
        print(f"Dados salvos com sucesso em {full_path}")
    except IOError as e:
        print(f"Ocorreu um erro ao salvar o arquivo: {e}")

def clean_local_stage(partition_key: str, action: str):
    if action.lower() not in ACTIONS:
        raise Exception("A ação deve estar listada nas ações")
    
    # Define o diretório base para o staging, convertendo para absoluto se necessário
    base_dir = Path(STAGING_AREA_PATH) if IS_ABSOLUTE_STAGING_AREA_PATH else Path.cwd() / STAGING_AREA_PATH
    
    dir_name = base_dir / action / partition_key
    
    # Verifica se o diretório existe antes de tentar removê-lo
    if dir_name.exists() and dir_name.is_dir():
        try:
            shutil.rmtree(dir_name)  # Remove o diretório e todo o seu conteúdo
            print(f"Diretório {dir_name} removido com sucesso.")
        except Exception as e:
            print(f"Ocorreu um erro ao tentar remover o diretório: {e}")
    else:
        print(f"O diretório {dir_name} não existe.")