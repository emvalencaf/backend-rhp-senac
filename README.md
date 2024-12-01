# backend-rhp-senac
Projeto de Residência do SENAC RHP

## Problema

O Real Hospital Português pediu uma solução que:

1. Envie dados de um formulário ao banco de dados.
2. Essa solução deve persistir os dados para o caso de falhas na conexão de dados e, em outro momento, que os dados sejam enviados.

## Desafios

1. A proposta da solução deve levar em conta os recursos do Real Hospital Português.

## Proposta de Solução

O software vai persistir os dados em uma estrutura (try catch) e, caso falhe, vai salvar os dados em um CSV localmente. Algo como:
```python
def push_data(data: DataSchema):
    try:
        # lógica para salvar dados no banco
    except Exception as e:
        print(e)
        local_save(data)
```
A principal vantagem dessa solução é o alto potencial e escalabilidade com poucos recursos. Cada máquina funcionaria como um *work node* em *cluster* sem precisar da configuração de um *cluster*. Acompanhado a essa solução, também será necessário fazer um CRON job para periodicamente (de preferência em horários de baixo pico) fazer o batch dos dados persistidos localmente em cada máquina.

## Rotas da API


# API Hospitalar

Essa API permite gerenciar dados hospitalares, incluindo unidades hospitalares, pacientes, leitos, profissionais e atendimentos. Utiliza o framework FastAPI e um banco de dados SQLite para armazenar informações.

## Instalação

1. Clone o repositório.
2. Instale as dependências com:
   ```bash
   pip install fastapi sqlalchemy pydantic sqlite3
   ```
3. Execute o servidor com o comando:
   ```bash
   uvicorn main:app --reload
   python -m uvicorn main:app --reload
   ```

## Tratamento de Error de Conexão e Banco de Dados

A persistência dos dados locais ocorrerá sempre que o banco de dados estiver fora do ar e se fará por meio da função `save_local_stage()` que recebe os parâmetros: `key_partition: str`, `action: str` e `data: dict`.

- A `key_partition` é a chave de partição e corresponde a entidade, por exemplo: `paciente`
- A `action` funciona como uma segunda chave de partição e corresponde a ação que se busca salvar, as quais podem ser: `create` ou `update`.
- A `data` refere-se aos dados que serão salvos localmente (em formato `json`).

Os dados serão persistidos em `json` com a seguinte partição `<action>/<entidade>/<ano>/<mes>/<dia>/<timestamp>.json` isso facilitará para a função *CRON Job* fazer o batch por `action` e `entity` e ordenar os registros.

É possível determinar por variáveis de ambiente em que local serão persistidos os dados localmente. Pelas seguintes variáveis que devem ser declaradas no arquivo `.env`:
```
STAGING_AREA_PATH=<caminho do repositório de dados local>
IS_ABSOLUTE_STAGING_AREA_PATH=<se o caminho é absoluto ou relativo>
```

## CRON JOB

O Cliente poderá configurar uma expressão cron para que o próprio backend faça uma operação em lote para persistir os dados locais no banco de dados. Para isso será necessário ir ao arquivo `.env` e preencher na variável `CRONTAB` a expressão que agenda a frequência em que os dados locais serão persistidos no banco de dados.

# 🌐 Endpoint disponível no Postman

## Você pode acessar todos os endpoints da API diretamente no Postman para facilitar os testes e a integração. 🚀

### Se você ainda não possui as configurações ou a coleção do Postman, entre em contato com o Time de Desenvolvimento 💻 para solicitar ajuda. Eles poderão:

### 📩 Compartilhar a coleção do Postman.
### 🔑 Fornecer as credenciais necessárias, se aplicável.
### 📋 Auxiliar na configuração manual, caso necessário.