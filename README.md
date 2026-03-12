# smart-image-search-firmato — Frontend

Interface web do buscador de imagens Firmato Móveis, construída com [Reflex](https://reflex.dev/).

Consome a API de catálogo (`/products`, `/search`) e oferece galeria paginada, busca semântica por texto e por imagem, e pré-visualização com download e cópia da imagem selecionada.

---

## O que o sistema faz

- **Galeria paginada** — lista produtos ativos consumindo `GET /products` da API de catálogo.
- **Busca por texto** — campo de busca com debounce de 500 ms que chama `POST /search?q=...` usando embeddings CLIP.
- **Busca por imagem** — upload de imagem (JPEG, PNG, WebP) que dispara `POST /search` com o arquivo, retornando os produtos mais similares.
- **Busca combinada** — texto + imagem enviados juntos; o backend combina os embeddings 50/50.
- **Pré-visualização** — painel lateral com zoom, botão de download e cópia da imagem para a área de transferência.

---

## Estrutura de pastas esperada

```
frontend/
├── app/
│   ├── __init__.py
│   ├── app.py           # instância rx.App + add_page
│   ├── api_client.py    # chamadas HTTP à API de catálogo
│   ├── rxconfig.py      # configuração do Reflex (portas, app_name)
│   ├── state.py         # State Reflex (lógica de negócio do frontend)
│   ├── pages/
│   │   └── home.py      # página principal (topbar, search panel, grid, preview)
│   └── styles/
│       └── home.py      # paleta de cores e estilos reutilizáveis
├── assets/              # arquivos estáticos (logo, favicon, etc.)
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## Pré-requisitos

- Python **3.12**
- Node.js **20+** (usado pelo Reflex para compilar o frontend)
- `venv` disponível (já vem com o Python 3.12)
- API de catálogo rodando em `http://localhost:8000`

---

## Como rodar localmente

### 1. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/smart-image-search-firmato-frontend.git
cd smart-image-search-firmato-frontend
```

### 2. Criar o ambiente virtual

```bash
python3.12 -m venv .venv
```

### 3. Ativar o ambiente virtual

**Linux / macOS:**
```bash
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

### 4. Instalar as dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Inicializar o Reflex

Na primeira vez, o Reflex baixa as dependências Node e gera a pasta `.web`:

```bash
reflex init
```

### 6. Configurar a URL da API

Abra `app/api_client.py` e ajuste a constante se necessário:

```python
API_BASE = "http://localhost:8000"
```

### 7. Rodar o frontend

```bash
reflex run
```

A interface estará disponível em: `http://localhost:3000`

> **Atenção:** a API de catálogo precisa estar rodando em `http://localhost:8000` para que a galeria e a busca funcionem. Consulte o README do repositório de backend para instruções de execução.

---

## Notas

- O Reflex sobe dois processos: o **servidor frontend** (Next.js, porta 3000) e o **backend Reflex** (FastAPI/websocket, porta 8001). Ambos são necessários para o funcionamento do State reativo.
- A variável `_image_bytes` no `State` é uma variável de instância privada (não sincronizada com o cliente), usada apenas para repassar os bytes da imagem ao backend Reflex durante a sessão.
- O debounce de 500 ms na busca por texto evita chamadas excessivas à API enquanto o usuário digita.

---

## Como subir em produção (Docker)

### Pré-requisitos

- Docker Engine 24+
- Docker Compose v2 (`docker compose` sem hífen)
- API de catálogo já rodando (ou configurada na mesma rede Docker)

### 1. Clonar e entrar na pasta

```bash
git clone https://github.com/seu-usuario/smart-image-search-firmato-frontend.git
cd smart-image-search-firmato-frontend
```

### 2. Ajustar a URL da API no Compose

Abra o `docker-compose.yml` e confirme a variável de ambiente:

```yaml
environment:
  - API_BASE=http://firmato-api:8000
```

> `firmato-api` é o nome do container da API na rede `firmato-net`. Se a API estiver em outro host, substitua pelo IP ou hostname correspondente.

### 3. Configurar a rede compartilhada

Se a API já foi iniciada com o `docker-compose.yml` do backend (que cria a rede `firmato-net`), descomente o bloco `external: true` no final do `docker-compose.yml` do frontend:

```yaml
networks:
  firmato-net:
    name: firmato-net
    external: true
```

Caso contrário, deixe como está — o Compose criará a rede automaticamente.

### 4. Build e subir

```bash
docker compose build
docker compose up -d
```

A interface estará disponível em `http://seu-servidor:3000`.

### Comandos úteis do dia a dia

```bash
# Rebuild após mudança de código
docker compose build && docker compose up -d

# Ver logs em tempo real
docker compose logs -f frontend

# Parar tudo
docker compose down
```

### Observação sobre o build

O estágio `builder` do Dockerfile executa `reflex init` e `reflex export` para pré-compilar o frontend estático durante o build da imagem. Isso torna o startup do container mais rápido, mas aumenta o tempo de build na primeira vez (download das dependências Node).
