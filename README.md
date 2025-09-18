# FastAPI AWS SAM

Esta aplicação serverless foi desenvolvida usando FastAPI e AWS SAM (Serverless Application Model), incluindo integração com SQS e DynamoDB.
Para começar, utilizei a base do AWS SAM + FastAPI de um artigo do Medium

## 📁 Estrutura do Projeto

```
fastapi-aws-sam/
├── src/                    # Código da aplicação Lambda
├── tests/                  # Testes automatizados
├── processor/              # Processamento de filas
├── template.yaml           # Template SAM com recursos AWS
├── samconfig.toml         # Configurações do SAM
├── docker-compose.yml     # Para desenvolvimento local
├── pyproject.toml         # Configurações do pytest
├── requirements.txt       # Dependências de produção
├── requirements-dev.txt   # Dependências de desenvolvimento
└── run_tests.bat         # Script para executar testes
```

## 🚀 Configuração Inicial

### Pré-requisitos
- Python 3.8+
- AWS CLI configurado
- SAM CLI instalado
- Docker instalado (opcional, para desenvolvimento local)

### Instalação de Dependências

```powershell
# Dependências de produção
pip install -r requirements.txt

# Dependências de desenvolvimento e teste
pip install -r requirements-dev.txt
```

## 🔨 Comandos de Build

### Build com SAM CLI (Recomendado)

```powershell
# Build usando container Docker (mais confiável)
sam build --use-container

# Build local (mais rápido, mas pode ter diferenças de ambiente)
sam build
```

### Build com Docker

```powershell
# Build da imagem Docker
docker build -t fastapi-aws-sam .

# Build com Docker Compose
docker-compose build
```

## 🚀 Comandos de Deploy

### Deploy Inicial (Primeira vez)

```powershell
# Deploy guiado (irá solicitar configurações)
sam deploy --guided

# Deploy com parâmetros específicos
sam deploy --guided --config-env qa
```

### Deploy para Ambiente QA

```powershell
# Deploy para QA usando configuração do samconfig.toml
sam deploy --config-env qa

# Deploy para QA com stack personalizado
sam deploy --config-env qa --stack-name minha-api-qa
```

### Deploy para Produção

```powershell
# Deploy para produção
sam deploy --config-env prod --stack-name fastapi-prod

# Deploy com confirmação de changeset
sam deploy --config-env prod --confirm-changeset
```

### Deploy Rápido (Após configuração inicial)

```powershell
# Deploy usando configurações salvas
sam deploy

# Deploy com override de ambiente
sam deploy --config-env prod
```

## 🧪 Comandos de Teste

### Executar Todos os Testes

```powershell
# Usando o script batch (Windows)
.\run_tests.bat

# Usando pytest diretamente
pytest tests/ -v

# Testes com relatório detalhado
pytest tests/ -v --tb=long
```

### Testes Específicos

```powershell
# Executar apenas testes unitários
pytest tests/ -m "unit" -v

# Executar apenas testes de integração
pytest tests/ -m "integration" -v

# Executar teste específico
pytest tests/test_auth.py -v

# Executar teste específico por nome
pytest tests/test_auth.py::test_valid_token -v
```

### Testes com Coverage

```powershell
# Instalar coverage
pip install coverage

# Executar testes com coverage
coverage run -m pytest tests/
coverage report
coverage html  # Gera relatório HTML
```

### Testes Avançados

```powershell
# Testes em paralelo (instalar pytest-xdist)
pip install pytest-xdist
pytest tests/ -n auto

# Testes com output em tempo real
pytest tests/ -v -s

# Parar no primeiro erro
pytest tests/ -x
```

## 💻 Desenvolvimento Local

### Executar API Localmente com SAM

```powershell
# Build primeiro
sam build --use-container

# Iniciar API localmente na porta 3000
sam local start-api

# API com porta customizada
sam local start-api --port 8080

# API com variáveis de ambiente personalizadas
sam local start-api --env-vars dev.env
```

### Executar com Docker Compose

```powershell
# Iniciar aplicação
docker-compose up

# Iniciar em background
docker-compose up -d

# Rebuild e iniciar
docker-compose up --build

# Parar aplicação
docker-compose down
```

### Executar FastAPI Diretamente

```powershell
# Desenvolvimento com reload automático
uvicorn src.main:app --reload --port 8000

# Com variáveis de ambiente
uvicorn src.main:app --reload --env-file dev.env
```

## 📊 Monitoramento e Logs

### Visualizar Logs da Lambda

```powershell
# Logs em tempo real
sam logs -n ApiLambdaFunction --stack-name fastapi-hello-world -t

# Logs das últimas 10 linhas
sam logs -n ApiLambdaFunction --stack-name fastapi-hello-world --tail

# Logs com filtro
sam logs -n ApiLambdaFunction --stack-name fastapi-hello-world --filter "ERROR"
```

### Invocar Função Lambda Localmente

```powershell
# Invocar função com evento personalizado
sam local invoke ApiLambdaFunction --event events/event.json

# Invocar com debug
sam local invoke ApiLambdaFunction --event events/event.json --debug
```

## 🔧 Comandos Úteis de Manutenção

### Limpeza

```powershell
# Limpar build artifacts
Remove-Item -Recurse -Force .aws-sam

# Limpar cache do pip
pip cache purge

# Limpar containers Docker
docker-compose down --volumes --remove-orphans
```

### Validação

```powershell
# Validar template SAM
sam validate

# Validar template com verbosidade
sam validate --debug
```

### Listagem de Recursos

```powershell
# Listar stacks CloudFormation
aws cloudformation list-stacks --query "StackSummaries[?StackStatus!='DELETE_COMPLETE'].{Name:StackName,Status:StackStatus}"

# Listar recursos do stack
aws cloudformation list-stack-resources --stack-name fastapi-hello-world
```

## 🗑️ Cleanup (Deletar Recursos)

```powershell
# Deletar stack completo
sam delete --stack-name fastapi-hello-world

# Deletar usando AWS CLI
aws cloudformation delete-stack --stack-name fastapi-hello-world

# Confirmar deleção
aws cloudformation wait stack-delete-complete --stack-name fastapi-hello-world
```

## 📚 Recursos Adicionais

- [AWS SAM Developer Guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [AWS Serverless Application Repository](https://aws.amazon.com/serverless/serverlessrepo/)
- [SAM CLI Reference](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-command-reference.html)

## 🐛 Troubleshooting

### Problemas Comuns

1. **Erro de permissões IAM**: Certifique-se de ter as permissões necessárias e use `--capabilities CAPABILITY_IAM`
2. **Timeout na Lambda**: Aumente o timeout no `template.yaml`
3. **Dependências não encontradas**: Use `sam build --use-container` para build em ambiente isolado
4. **Erro de sintaxe no template**: Use `sam validate` para verificar o template

### Debug

```powershell
# Build com debug
sam build --debug

# Deploy com debug
sam deploy --debug

# Logs detalhados
sam logs -n ApiLambdaFunction --stack-name fastapi-hello-world --start-time '10 min ago' --debug
```
