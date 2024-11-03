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
   ```

## Endpoints

### 1. Unidade Hospitalar

#### Criar Unidade
- **POST** `/unidade/`
- **Exemplo de JSON**:
  ```json
  {
    "nome": "Hospital Central",
    "localizacao": "Centro"
  }
  ```
- **Resposta**:
  ```json
  {
    "id_unidade": 1,
    "nome": "Hospital Central",
    "localizacao": "Centro"
  }
  ```

#### Listar Unidades
- **GET** `/unidade/`
- **Resposta**:
  ```json
  [
    {
      "id_unidade": 1,
      "nome": "Hospital Central",
      "localizacao": "Centro"
    }
  ]
  ```

#### Atualizar Unidade
- **PUT** `/unidade/{id_unidade}`
- **Exemplo de JSON**:
  ```json
  {
    "nome": "Hospital Atualizado",
    "localizacao": "Zona Norte"
  }
  ```

#### Deletar Unidade
- **DELETE** `/unidade/{id_unidade}`

### 2. Pacientes

#### Criar Paciente
- **POST** `/paciente/`
- **Exemplo de JSON**:
  ```json
  {
  "nome": "João da Silva",
  "data_nascimento": "1980-05-15",
  "endereco": "Rua das Flores, 123",
  "cep": "12345-678",
  "nome_mae": "Maria da Silva",
  "id_leito": 3
  }
  ```

#### Listar Pacientes
- **GET** `/paciente/`
  
#### Atualizar Paciente
- **PUT** `/paciente/{id_paciente}`
  
#### Deletar Paciente
- **DELETE** `/paciente/{id_paciente}`

### 3. Leitos

#### Criar Leito
- **POST** `/leito/`
- **Exemplo de JSON**:
  ```json
  {
    "tipo": "UTI",
    "ocupado": 0
  }
  ```

#### Listar Leitos
- **GET** `/leito/`

#### Atualizar Leito
- **PUT** `/leito/{id_leito}`
  
#### Deletar Leito
- **DELETE** `/leito/{id_leito}`

### 4. Profissionais

#### Criar Profissional
- **POST** `/profissional/`
- **Exemplo de JSON**:
  ```json
  {
    "nome": "Dra. Maria",
    "setor": "Cardiologia",
    "funcao": "Médico"
  }
  ```

#### Listar Profissionais
- **GET** `/profissional/`

#### Atualizar Profissional
- **PUT** `/profissional/{id_profissional}`
  
#### Deletar Profissional
- **DELETE** `/profissional/{id_profissional}`

### 5. Atendimentos

#### Criar Atendimento
- **POST** `/atendimento/`
- **Exemplo de JSON**:
  ```json
  {
    "data_hora": "2023-07-14T15:30:00",
    "tipo": "Emergência",
    "origem": "Ambulância",
    "convenio": "Privado",
    "id_paciente": 1,
    "id_profissional": 2
  }
  ```

#### Listar Atendimentos
- **GET** `/atendimento/`

#### Atualizar Atendimento
- **PUT** `/atendimento/{id_atendimento}`
  
#### Deletar Atendimento
- **DELETE** `/atendimento/{id_atendimento}`

## Estrutura de Dados para Testes

Aqui estão exemplos de dados em JSON que podem ser usados para teste da API.

### Exemplo de Dados

```json
{
  "unidades": [
    { "nome": "Hospital Central", "localizacao": "Centro" }
  ],

  "pacientes": [
      {
    "nome": "João da Silva",
    "data_nascimento": "1980-05-15",
    "endereco": "Rua das Flores, 123",
    "cep": "12345-678",
    "nome_mae": "Maria da Silva",
    "id_leito": 3
      }
  ],

  "leitos": [
    { "tipo": "UTI", "ocupado": 0 }
  ],

  "profissionais": [
    { "nome": "Dra. Maria", "setor": "Cardiologia", "funcao": "Médico" }
  ],
  
  "atendimentos": [
    {
      "data_hora": "2023-07-14T15:30:00",
      "tipo": "Emergência",
      "origem": "Ambulância",
      "convenio": "Privado",
      "id_paciente": 1,
      "id_profissional": 1
    }
  ]
}
```
