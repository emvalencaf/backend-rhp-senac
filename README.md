# backend-rhp-senac
Projeto de Residência do SENAC RHP

## Problema

O Real Hospital Português pediu uma solução que:

1. Envie dados de um formulário ao banco de dados.
2. Essa solução deve persistir os dados para o caso de falhas na conexão de dados e, em outro momento, que os dados sejam enviados.

## Desafios

1. A proposta da solução deve levar em conta os recursos do Real Hospital Português

## Proposta de Solução

O software vai persistir os dados em uma estrutura (try catch) e, caso falhe, vai salvar os dados em um csv localmente, algo como:
```
def push_data(data: DataSchema):
  try:
    # lógica para salvar dados locais
  except Exception as e:
    print(e)
    local_save(data)
```
A principal vantagem dessa solução é o alto potencial e escalabilidade com poucos recursos. Cada máquina funcionaria como um *work node* em *cluster* sem precisar a configuração de um *cluster*.
Acompanhado a essa solução também será necessário fazer um CRON job para peridiocamente (de preferência em horários de baixo pico) fazer o batch dos dados persitidos localmente em cada máquina.


