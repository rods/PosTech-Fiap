# PosTech FIAP - Book Recommendation API

API serverless para repositório e recomendação de livros, desenvolvida como projeto da Pós-Graduação FIAP.

## 📋 Descrição do Projeto

Sistema de gerenciamento e recomendação de livros com arquitetura cloud-native na AWS. A aplicação realiza scraping automatizado de dados de livros, armazena em DynamoDB e disponibiliza APIs REST para consulta e recomendações baseadas em Machine Learning.

## 🏗️ Arquitetura

![Arquitetura](https://github.com/rods/PosTech-Fiap/blob/main/books_scraper_architecture.png)

### Componentes AWS:
- **ECS (Fargate)**: Hospedagem da API conteinerizada
- **Lambda**: Scraping de dados e processamento de eventos S3
- **DynamoDB**: Banco de dados NoSQL (tabelas Books e users)
- **S3**: Armazenamento de arquivos CSV do scraping (bucket: `fiap-postech-scrape-book`)
- **EventBridge**: Agendamento automático do scraping
- **ECR**: Registry de imagens Docker
- **CloudWatch**: Logs e métricas

### Fluxo de Dados:
1. EventBridge dispara Lambda de scraping periodicamente
2. Lambda salva CSV no S3
3. Trigger S3 aciona Lambda que insere dados no DynamoDB
4. API ECS consulta DynamoDB para servir requisições
5. Dashboard Streamlit consome métricas do CloudWatch

## 📁 Estrutura do Projeto


PosTech-Fiap/
├── app/
│   ├── routers/          # Endpoints da API
│   ├── core/             # Autenticação e configurações
│   ├── internal/         # Modelo de ML para recomendações
│   └── models/           # Modelos de dados (Pydantic)
├── dashboard/            # Dashboard Streamlit
├── requirements.txt      # Dependências Python
├── Dockerfile           # Imagem Docker da aplicação
└── .github/workflows/   # CI/CD GitHub Actions

## 🚀 Pré-requisitos

- Python 3.11
- AWS CLI v3
- Docker (para build local)
- Conta AWS configurada

## ⚙️ Configuração

### 1. Configurar AWS CLI

bash
aws configure
AWS Access Key ID: [sua-key]
AWS Secret Access Key: [seu-secret]
Default region name: us-east-2
Default output format: json

### 2. Criar Tabelas DynamoDB

**Tabela Books:**
bash
aws dynamodb create-table \
   --table-name Books \
   --attribute-definitions AttributeName=id,AttributeType=N \
   --key-schema AttributeName=id,KeyType=HASH \
   --billing-mode PAY_PER_REQUEST \
   --region us-east-2

**Tabela users:**
bash
aws dynamodb create-table \
   --table-name users \
   --attribute-definitions AttributeName=id,AttributeType=N \
   --key-schema AttributeName=id,KeyType=HASH \
   --billing-mode PAY_PER_REQUEST \
   --region us-east-2

### 3. Variáveis de Ambiente

Criar arquivo `.env` na raiz do projeto:

env
SECRET_KEY=seu-secret-key-gerado-aqui-minimo-32-caracteres
AWS_DEFAULT_REGION=us-east-2

Gerar SECRET_KEY seguro:
bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

## 💻 Execução Local

### 1. Clonar Repositório

bash
git clone https://github.com/rods/PosTech-Fiap.git
cd PosTech-Fiap

### 2. Criar Virtual Environment

bash
python3.11 -m venv venv
source venv/bin/activate (Linux/Mac) 
ou 
venv\Scripts\activate (Windows)

### 3. Instalar Dependências

bash
pip install -r requirements.txt

### 4. Executar API

bash
uvicorn app.main:app --reload

A API estará disponível em: `http://localhost:8000`

### 5. Executar Dashboard (Opcional)

bash
streamlit run dashboard/app.py --server.port 8500

Dashboard disponível em: `http://localhost:8500`

## 📚 Documentação da API

### Swagger UI
Acesse a documentação interativa em: `http://localhost:8000/docs`

### Principais Endpoints

#### 1. Health Check
http
GET /api/v1/health

**Response:**
json
{
 "status": "ok"
}

---

#### 2. Autenticação

http
POST /api/v1/auth/login
Content-Type: application/json

{
 "username": "seu-usuario",
 "password": "sua-senha"
}

**Response:**
json
{
 "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
 "token_type": "bearer",
 "message": "Login successful"
}

---

#### 3. Criar Livro

http
POST /api/v1/books
Authorization: Bearer {token}
Content-Type: application/json

{
 "id": 1,
 "title": "Clean Code",
 "price": 89.90,
 "rating": 4.8,
 "availability": true,
 "category": "Programming"
}

**Response (201):**
json
{
 "message": "Livro criado com sucesso",
 "id": 1,
 "created_by": "usuario"
}

**Possíveis Erros:**
- `401`: Token inválido ou ausente
- `409`: Livro com esse ID já existe
- `500`: Erro interno do servidor

---

#### 4. Buscar Livros

http
GET /api/v1/books/search?title=Clean&category=Programming
Authorization: Bearer {token}

**Parâmetros de Query:**
- `title` (opcional): Busca parcial no título
- `category` (opcional): Busca exata por categoria
- Pelo menos um parâmetro é obrigatório

**Response:**
json
[
 {
   "id": 1,
   "title": "Clean Code",
   "price": 89.90,
   "rating": 4.8,
   "availability": true,
   "category": "Programming"
 }
]

**Possíveis Erros:**
- `400`: Nenhum parâmetro de busca fornecido
- `401`: Token inválido ou ausente
- `500`: Erro interno do servidor

---

### Autenticação

Todas as rotas POST requerem autenticação JWT.

**Como usar:**
1. Faça login em `/auth/login` para obter o token
2. Inclua o token no header: `Authorization: Bearer {seu-token}`
3. Token expira em 30 minutos

## 🔄 CI/CD

### Deploy Automático

O deploy é automatizado via GitHub Actions:

1. **Push na branch `main`** dispara o workflow
2. **Build** da imagem Docker
3. **Push** para Amazon ECR
4. **Deploy** no ECS Fargate

### Workflow (.github/workflows/deploy.yml)

## 🤖 Sistema de Scraping

### Funcionamento:
1. **EventBridge** agenda execução periódica
2. **Lambda Scraper** coleta dados do site fonte
3. Salva arquivo CSV no bucket S3 `fiap-postech-scrape-book`
4. **Trigger S3** aciona Lambda de processamento
5. Lambda insere/atualiza registros no DynamoDB

## 🧠 Modelo de Recomendação

Localizado em `/app/internal/`, o modelo de Machine Learning analisa:
- Histórico de buscas
- Ratings dos livros
- Categorias relacionadas
- Padrões de disponibilidade

Retorna recomendações.

## 📊 Dashboard

Dashboard Streamlit para visualização de logs e métricas:
- Logs
- Requests (acessos, erros, cache)
- Métricas de serviço
- Logs do CloudWatch

**Acesso:** URL fornecida na documentação do trabalho (por segurança)

## 🔒 Segurança

- Autenticação JWT com expiração de 30 minutos
- Validação de tokens em todas as rotas protegidas
- IAM roles com permissões mínimas necessárias

## 📝 Notas Importantes

- Região AWS: **us-east-2** (Ohio)
- Tabelas DynamoDB usam billing mode **PAY_PER_REQUEST**
- Logs disponíveis no CloudWatch Logs
- Imagens Docker armazenadas no ECR privado

## 👥 Autores

Projeto desenvolvido como requisito da Pós-Graduação FIAP.

## 📄 Licença

Projeto acadêmico - FIAP 2025
