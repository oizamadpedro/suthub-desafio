# Age Groups and Enrollment API

Este projeto implementa uma API para gerenciamento de grupos etários e matrículas com autenticação Basic Auth.

## Autenticação

A API utiliza Basic Auth com credenciais estáticas definidas no arquivo `src/auth_users.txt`.

### Tipos de Usuários

- **Configuration Users** (`config_*`): Podem gerenciar grupos etários e realizar matrículas
- **Final Users** (`final_*`): Podem apenas realizar matrículas e consultar dados

### Credenciais Padrão

```
# Configuration Users
config_admin:admin123
config_user:user456

# Final Users
final_user1:password1
final_user2:password2
```

## Endpoints

### Configuration User Endpoints (Gerenciamento de Grupos Etários)

#### POST /config/age-groups
Criar novo grupo etário
- **Auth**: Configuration User
- **Body**: 
```json
{
  "name": "Crianças",
  "min_age": 0,
  "max_age": 12
}
```

#### GET /config/age-groups
Listar todos os grupos etários
- **Auth**: Configuration User

#### GET /config/age-groups/{id}
Obter grupo etário específico
- **Auth**: Configuration User

#### PUT /config/age-groups/{id}
Atualizar grupo etário
- **Auth**: Configuration User
- **Body**: 
```json
{
  "name": "Adolescentes",
  "min_age": 13,
  "max_age": 17
}
```

#### DELETE /config/age-groups/{id}
Deletar grupo etário
- **Auth**: Configuration User

### Final User Endpoints (Matrículas)

#### POST /enroll
Criar nova matrícula
- **Auth**: Final User ou Configuration User
- **Body**: 
```json
{
  "name": "João Silva Santos",
  "age": 25,
  "cpf": "12345678901"
}
```

#### GET /enrollments
Listar todas as matrículas
- **Auth**: Final User ou Configuration User

#### GET /enrollments/{cpf}
Obter matrícula por CPF
- **Auth**: Final User ou Configuration User

#### DELETE /enrollments/{cpf}
Deletar matrícula por CPF
- **Auth**: Final User ou Configuration User

### Endpoint Legacy

#### POST /enroll-legacy
Endpoint de compatibilidade com versão anterior (envia para SQS)

## Regras de Negócio

1. **Grupos Etários**:
   - Cada grupo tem nome, idade mínima e máxima
   - Não pode haver sobreposição de faixas etárias entre grupos
   - min_age deve ser <= max_age

2. **Matrículas**:
   - Nome deve ter pelo menos nome e sobrenome (mínimo 2 palavras)
   - CPF deve ser válido (validação com dígitos verificadores)
   - Idade deve estar dentro de algum grupo etário cadastrado
   - CPF deve ser único (não pode ter matrículas duplicadas)

## Validações

### CPF
- Formato: 11 dígitos numéricos
- Validação completa com dígitos verificadores
- Não aceita CPFs com todos os dígitos iguais

### Nome
- Mínimo 2 palavras (nome e sobrenome)
- Cada palavra deve ter pelo menos 2 caracteres
- Apenas letras e espaços são permitidos

### Idades
- Deve estar entre 0 e 120 anos
- Deve corresponder a algum grupo etário cadastrado

## Estrutura de Dados

### Modelos Pydantic (Request/Response)
- `AgeGroupCreateRequest`
- `AgeGroupUpdateRequest`
- `EnrollmentRequest`
- `AgeGroupResponse`
- `EnrollmentResponse`

### Dataclasses (Processamento Interno)
- `AgeGroup`
- `Enrollment`

## Banco de Dados

O projeto utiliza DynamoDB com duas tabelas:
- `age-groups`: Armazena os grupos etários
- `enrollments`: Armazena as matrículas

## Exemplo de Uso com curl

```bash
# Criar grupo etário
curl -X POST "http://localhost:8000/config/age-groups" \
  -H "Content-Type: application/json" \
  -u "config_admin:admin123" \
  -d '{
    "name": "Adultos",
    "min_age": 18,
    "max_age": 65
  }'

# Criar matrícula
curl -X POST "http://localhost:8000/enroll" \
  -H "Content-Type: application/json" \
  -u "final_user1:password1" \
  -d '{
    "name": "Maria Silva Santos",
    "age": 25,
    "cpf": "12345678901"
  }'
```

## Variáveis de Ambiente

- `AGE_GROUPS_TABLE`: Nome da tabela DynamoDB para grupos etários (padrão: "age-groups")
- `ENROLLMENTS_TABLE`: Nome da tabela DynamoDB para matrículas (padrão: "enrollments")
- `QUEUE_URL`: URL da fila SQS para compatibilidade com versão anterior
- `ENV`: Ambiente de execução (dev, qa, prod)