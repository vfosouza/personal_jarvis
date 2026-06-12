# Personal Jarvis

Personal Jarvis é um projeto de assistente inteligente local baseado em **RAG — Retrieval-Augmented Generation**.  
O objetivo do projeto é permitir consultas em linguagem natural sobre repositórios de código, arquivos e documentação, utilizando embeddings, busca vetorial no Qdrant e geração de respostas com modelo local executado via Ollama.

O sistema é composto por dois serviços principais:

- **API**: expõe endpoints HTTP para interação com o assistente.
- **Indexer**: percorre diretórios de repositórios, lê arquivos suportados, divide o conteúdo em chunks, gera embeddings e indexa os dados no Qdrant.

Além disso, o projeto utiliza:

- **Ollama** para execução local do modelo de linguagem.
- **Qdrant** como banco vetorial.
- **Sentence Transformers** para geração de embeddings.
- **Docker Compose** para orquestração dos serviços.

---

## Sumário

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Descrição dos Diretórios](#descrição-dos-diretórios)
- [Fluxo de Funcionamento](#fluxo-de-funcionamento)
- [Serviços Docker](#serviços-docker)
- [Configuração](#configuração)
- [API](#api)
- [Indexer](#indexer)
- [Busca Semântica e Busca por Referência](#busca-semântica-e-busca-por-referência)
- [Modelo de Embeddings](#modelo-de-embeddings)
- [Banco Vetorial Qdrant](#banco-vetorial-qdrant)
- [Modelo LLM via Ollama](#modelo-llm-via-ollama)
- [Como Executar o Projeto](#como-executar-o-projeto)
- [Como Indexar Repositórios](#como-indexar-repositórios)
- [Exemplos de Uso](#exemplos-de-uso)
- [Dependências](#dependências)
- [Observações Importantes](#observações-importantes)
- [Melhorias Futuras](#melhorias-futuras)

---

## Visão Geral

O Personal Jarvis funciona como um assistente especializado em análise de código e engenharia de dados.  
Ele permite perguntar sobre conteúdos previamente indexados, como:

- Onde determinado termo aparece.
- Em qual arquivo uma função, classe ou conceito foi utilizado.
- Explicações sobre trechos de código.
- Relações entre serviços, repositórios e arquivos.
- Dúvidas gerais respondidas com base no contexto indexado.

O projeto combina duas estratégias de recuperação de informação:

1. **Busca semântica por embeddings**  
   Utilizada para perguntas conceituais ou explicativas.

2. **Busca textual por palavra-chave/referência**  
   Utilizada para perguntas como:
   - "onde usei X?"
   - "quem chama Y?"
   - "em qual arquivo aparece Z?"
   - "localize determinada dependência"

---

## Arquitetura

A arquitetura geral do projeto pode ser representada da seguinte forma:
text Usuário | v API FastAPI | |-- Identifica tipo da pergunta | |-- Busca semântica por embedding | | | v | Qdrant | |-- Busca por referência/palavra-chave | | | v | Qdrant | v Prompt Builder | v Ollama | v Resposta ao usuário

O processo de indexação ocorre separadamente:
text Diretórios de repositórios | v Indexer | |-- Carrega arquivos suportados |-- Ignora diretórios configurados |-- Divide arquivos em chunks |-- Gera embeddings | v Qdrant

---

## Tecnologias Utilizadas

O projeto utiliza as seguintes tecnologias principais:

- **Python**
- **FastAPI**
- **Uvicorn**
- **Requests**
- **Qdrant Client**
- **Sentence Transformers**
- **Ollama**
- **Docker**
- **Docker Compose**

---

## Estrutura do Projeto

Estrutura atual do projeto:
text personal_jarvis ├── .venv ├── api │ ├── app │ │ ├── repositories │ │ │ ├── **init**.py │ │ │ └── qdrant_repository.py │ │ ├── routes │ │ │ ├── **init**.py │ │ │ └── chat.py │ │ ├── services │ │ │ ├── **init**.py │ │ │ ├── ollama_client.py │ │ │ ├── prompt_builder.py │ │ │ ├── rag.py │ │ │ └── search.py │ │ ├── **init**.py │ │ ├── config.py │ │ ├── embeddings.py │ │ └── main.py │ ├── Dockerfile │ └── requirements.txt ├── indexer │ ├── app │ │ ├── **init**.py │ │ ├── chunking.py │ │ ├── config.py │ │ ├── embeddings.py │ │ ├── file_loader.py │ │ ├── index_repo.py │ │ └── qdrant_store.py │ ├── **init**.py │ ├── Dockerfile │ └── requirements.txt ├── repositories ├── .gitignore ├── docker-compose.yaml ├── pyproject.toml └── README.md

---

## Descrição dos Diretórios

### Raiz do projeto

#### `personal_jarvis/`

Diretório principal do projeto.  
Contém os serviços da aplicação, configurações Docker, dependências e documentação.

Arquivos principais:

- `docker-compose.yaml`: define os containers da aplicação.
- `pyproject.toml`: arquivo de configuração do projeto Python.
- `.gitignore`: define arquivos e diretórios ignorados pelo Git.
- `README.md`: documentação principal do projeto.

---

## Diretório `api`

O diretório `api` contém a aplicação HTTP responsável por receber perguntas do usuário, recuperar contexto no Qdrant, montar prompts e consultar o modelo LLM via Ollama.
text api ├── app ├── Dockerfile └── requirements.txt

### `api/Dockerfile`

Define a imagem Docker da API.

Responsabilidades:

- Utilizar imagem base Python.
- Definir `/app` como diretório de trabalho.
- Instalar dependências.
- Copiar os arquivos da aplicação.
- Iniciar o servidor FastAPI com Uvicorn.

Comando executado no container:
bash uvicorn app.main:app --host 0.0.0.0 --port 8000

### `api/requirements.txt`

Lista as dependências necessárias para execução da API.

Dependências principais:
text fastapi uvicorn requests qdrant-client sentence-transformers

---

## Diretório `api/app`

Contém o código-fonte principal da API.
text api/app ├── repositories ├── routes ├── services ├── **init**.py ├── config.py ├── embeddings.py └── main.py

### `api/app/main.py`

Arquivo de entrada da aplicação FastAPI.

Responsabilidades:

- Criar a instância da aplicação.
- Registrar as rotas.
- Expor endpoint básico de health check.

Endpoint raiz:
http GET /
Resposta esperada: json { "status": "running" }

---

### `api/app/config.py`

Arquivo de configuração da API.

Contém informações como:

- URL do Ollama.
- Modelo utilizado no Ollama.
- Host e porta do Qdrant.
- Nome da collection vetorial.
- Padrões utilizados para identificar perguntas de busca por referência.

Configurações principais:
python OLLAMA_URL = "[http://ollama:11434](http://ollama:11434)" OLLAMA_MODEL = "qwen2.5:1.5b" QDRANT_HOST = "qdrant" QDRANT_PORT = 6333 COLLECTION_NAME = "repositories"

Também define termos usados para detectar consultas do tipo referência, por exemplo:
text onde usei onde foi usado onde aparece em qual arquivo quem usa quem chama referência buscar procure localize repository service

Esses padrões ajudam o sistema a decidir se deve usar busca textual direta ou busca semântica por embedding.

---

### `api/app/embeddings.py`

Responsável por carregar o modelo de embeddings e gerar vetores a partir de textos.

Modelo utilizado:
text sentence-transformers/all-MiniLM-L6-v2

A função principal gera uma representação vetorial do texto recebido, retornando uma lista numérica compatível com o Qdrant.

---

## Diretório `api/app/repositories`

Contém classes e funções responsáveis pela comunicação da API com fontes de dados externas.
text api/app/repositories ├── **init**.py └── qdrant_repository.py

### `api/app/repositories/qdrant_repository.py`

Camada de acesso ao Qdrant.

Responsabilidades esperadas:

- Criar cliente Qdrant.
- Executar buscas vetoriais.
- Executar buscas por palavra-chave.
- Recuperar documentos/chunks indexados.
- Servir como abstração entre a lógica RAG e o banco vetorial.

Essa separação evita que os serviços da API dependam diretamente dos detalhes internos do Qdrant.

---

## Diretório `api/app/routes`

Contém as rotas HTTP da API.
text api/app/routes ├── **init**.py └── chat.py

### `api/app/routes/chat.py`

Define os endpoints relacionados ao chat ou perguntas ao assistente.

Responsabilidades esperadas:

- Receber perguntas do usuário.
- Encaminhar a pergunta para a camada RAG.
- Retornar a resposta gerada pelo modelo.
- Tratar requisições HTTP relacionadas ao assistente.

---

## Diretório `api/app/services`

Contém a lógica de negócio da API.

text api/app/services ├── **init**.py ├── ollama_client.py ├── prompt_builder.py ├── rag.py └── search.py

### `api/app/services/ollama_client.py`

Responsável pela comunicação com o Ollama.

Responsabilidades esperadas:

- Enviar prompts para o modelo configurado.
- Receber respostas geradas pelo LLM.
- Centralizar chamadas HTTP para o serviço Ollama.

O modelo configurado no projeto é:
text qwen2.5:1.5b

---

### `api/app/services/prompt_builder.py`

Responsável por construir os prompts enviados ao LLM.

Existem dois tipos principais de prompt:

#### Prompt para perguntas gerais

Utilizado quando a pergunta será respondida com base em contexto semântico recuperado via embeddings.

Características:

- Instrui o modelo a responder como especialista em engenharia de dados.
- Determina que a resposta deve usar apenas o contexto fornecido.
- Inclui contexto, pergunta e espaço para resposta.

#### Prompt para busca por referência

Utilizado quando o usuário quer localizar uso de termos, arquivos, classes, serviços ou dependências.

Características:

- Instrui o modelo a responder como especialista em análise de código.
- Solicita que cada ocorrência contenha:
   - arquivo;
   - trecho encontrado;
   - explicação do uso.
- Proíbe inventar arquivos ou código não presentes no contexto.

---

### `api/app/services/rag.py`

Serviço central de RAG da API.

Responsabilidades:

- Identificar o tipo de busca.
- Recuperar contexto no Qdrant.
- Construir prompts apropriados.
- Enviar prompt ao Ollama.
- Retornar a resposta final.

Principais fluxos:

#### Busca semântica

Usada para perguntas abertas ou explicativas.

Exemplo:
text Explique como funciona o processo de indexação.

Fluxo:
text Pergunta -> geração/uso de embedding -> busca similar no Qdrant -> montagem de contexto -> prompt geral -> Ollama -> resposta

#### Busca por referência

Usada para localizar termos no conteúdo indexado.

Exemplo:
text Onde usei qdrant?
Fluxo:
text Pergunta -> extração do termo buscado -> varredura dos pontos no Qdrant -> agrupamento por arquivo -> extração de trechos próximos ao termo -> prompt de referência -> Ollama -> resposta

O serviço também limita o tamanho do contexto para evitar prompts muito grandes.

---

### `api/app/services/search.py`

Responsável por funções auxiliares de busca.

Responsabilidades esperadas:

- Detectar se uma pergunta é uma busca por referência.
- Extrair o termo principal da pergunta.
- Auxiliar na escolha entre busca semântica e busca textual.

---

## Diretório `indexer`

O diretório `indexer` contém a aplicação responsável por indexar arquivos dos repositórios configurados.
text indexer ├── app ├── **init**.py ├── Dockerfile └── requirements.txt

### `indexer/Dockerfile`

Define a imagem Docker do indexador.

Responsabilidades esperadas:

- Utilizar imagem base Python.
- Instalar dependências.
- Copiar arquivos do indexador.
- Executar rotina de indexação.

---

### `indexer/requirements.txt`

Lista as dependências necessárias para o serviço de indexação.

As dependências tendem a incluir bibliotecas como:

text qdrant-client sentence-transformers

Também podem incluir bibliotecas auxiliares para leitura de arquivos e processamento de texto.

---

## Diretório `indexer/app`

Contém o código principal do indexador.

text indexer/app ├── **init**.py ├── chunking.py ├── config.py ├── embeddings.py ├── file_loader.py ├── index_repo.py └── qdrant_store.py

---

### `indexer/app/config.py`

Arquivo de configuração do indexador.

Configurações principais:
python QDRANT_HOST = "qdrant" QDRANT_PORT = 6333 COLLECTION_NAME = "repositories" CHUNK_SIZE = 2000 CHUNK_OVERLAP = 200 BATCH_SIZE = 32 MAX_FILE_SIZE = 500_000

#### Extensões suportadas

O indexador processa arquivos com extensões configuradas em `SUPPORTED_EXTENSIONS`.

Extensões suportadas:
text .py .sql .yml .yaml .json .md .txt .tf .sh .cfg .ini

#### Diretórios ignorados

O indexador ignora diretórios que normalmente não devem ser processados, como:
text .git .idea .vscode venv .venv target **pycache** node_modules build dist .terraform dbt_packages .pytest_cache .mypy_cache .next

Isso evita indexar arquivos temporários, dependências, artefatos de build e diretórios internos de ferramentas.

---

### `indexer/app/embeddings.py`

Responsável por gerar embeddings dos chunks de texto durante a indexação.

O objetivo é converter cada trecho de arquivo em um vetor numérico para armazenamento no Qdrant.

---

### `indexer/app/chunking.py`

Responsável por dividir arquivos grandes em partes menores.

Configurações relacionadas:
python CHUNK_SIZE = 2000 CHUNK_OVERLAP = 200

#### Chunk size

Define o tamanho máximo aproximado de cada pedaço de texto.

#### Chunk overlap

Define a sobreposição entre chunks consecutivos.  
Isso ajuda a preservar contexto entre partes próximas do mesmo arquivo.

Exemplo conceitual:
text Arquivo original | |-- Chunk 1: caracteres 0 a 2000 |-- Chunk 2: caracteres 1800 a 3800 |-- Chunk 3: caracteres 3600 a 5600

---

### `indexer/app/file_loader.py`

Responsável por percorrer diretórios e carregar arquivos.

Responsabilidades esperadas:

- Percorrer repositórios configurados.
- Ignorar diretórios definidos em `IGNORE_DIRS`.
- Filtrar arquivos por extensão.
- Ignorar arquivos maiores que `MAX_FILE_SIZE`.
- Ler o conteúdo dos arquivos.
- Retornar metadados como:
   - caminho do arquivo;
   - nome do arquivo;
   - repositório;
   - conteúdo.

---

### `indexer/app/index_repo.py`

Arquivo principal da rotina de indexação.

Responsabilidades esperadas:

- Coordenar o processo de indexação.
- Carregar arquivos dos repositórios.
- Dividir conteúdo em chunks.
- Gerar embeddings.
- Enviar dados ao Qdrant.
- Controlar indexação em lote.

Fluxo esperado:
text index_repo.py | |-- carregar arquivos |-- dividir em chunks |-- gerar embeddings |-- montar payloads |-- salvar no Qdrant

---

### `indexer/app/qdrant_store.py`

Camada responsável por gravar dados no Qdrant.

Responsabilidades esperadas:

- Criar ou validar collection.
- Configurar dimensão dos vetores.
- Inserir pontos vetoriais.
- Enviar payloads contendo metadados dos arquivos.
- Trabalhar com batches para melhor performance.

---

## Diretório `repositories`

Diretório reservado para repositórios ou arquivos que podem ser indexados.
text repositories
No `docker-compose.yaml`, o serviço `indexer` monta diretórios locais dentro de `/repositories`.

Exemplo:
yaml volumes:
- /Users/vfosouza/Workspace:/repositories/Workspace
- /Users/vfosouza/Workspace_Servier:/repositories/Workspace_Servier

Isso significa que os repositórios locais são disponibilizados dentro do container do indexador para leitura e indexação.

---

## Diretório `.venv`

Ambiente virtual Python local.
text .venv

Esse diretório normalmente contém:

- interpretador Python isolado;
- bibliotecas instaladas;
- scripts do ambiente virtual.

Ele não deve ser versionado no Git.

---

## Fluxo de Funcionamento

O fluxo completo do sistema pode ser dividido em duas fases.

---

### 1. Fase de Indexação

A indexação prepara os dados para consulta.

text Repositórios locais | v Indexer | |-- lê arquivos suportados |-- ignora diretórios não relevantes |-- divide conteúdo em chunks |-- gera embeddings |-- salva vetores e metadados | v Qdrant

Cada chunk indexado pode conter payloads como:

- conteúdo textual;
- caminho do arquivo;
- nome do arquivo;
- nome do repositório;
- metadados adicionais.

---

### 2. Fase de Pergunta e Resposta

Após a indexação, o usuário pode fazer perguntas à API.

text Usuário | v Endpoint de chat | v Serviço RAG | |-- identifica tipo da pergunta |-- recupera contexto no Qdrant |-- monta prompt |-- envia ao Ollama | v Resposta

---

## Serviços Docker

O projeto utiliza `docker-compose.yaml` para subir os serviços necessários.

Serviços definidos:
text ollama ollama-init qdrant api indexer

---

### Serviço `ollama`

Executa o servidor Ollama.
yaml ollama: image: ollama/ollama container_name: ollama ports: - "11434:11434" volumes: - ollama_data:/root/.ollama restart: unless-stopped

Responsabilidades:

- Disponibilizar API local do Ollama na porta `11434`.
- Armazenar modelos baixados no volume `ollama_data`.

---

### Serviço `ollama-init`

Serviço auxiliar para baixar o modelo utilizado.
yaml ollama-init: image: ollama/ollama container_name: ollama-init depends_on: - ollama volumes: - ollama_data:/root/.ollama entrypoint: - /bin/sh - -c - | echo "Aguardando Ollama..." sleep 15 ollama pull qwen2.5:1.5b echo "Modelo carregado."

Responsabilidades:

- Aguardar inicialização do Ollama.
- Baixar o modelo `qwen2.5:1.5b`.
- Compartilhar o modelo com o container principal via volume.

---

### Serviço `qdrant`

Executa o banco vetorial Qdrant.
yaml qdrant: image: qdrant/qdrant container_name: qdrant ports: - "6333:6333" volumes: - qdrant_data:/qdrant/storage

Responsabilidades:

- Armazenar vetores de embeddings.
- Permitir buscas por similaridade.
- Persistir dados no volume `qdrant_data`.

---

### Serviço `api`

Executa a API FastAPI.
yaml api: build: ./api ports: - "8000:8000" depends_on: - ollama - qdrant

Responsabilidades:

- Receber perguntas do usuário.
- Consultar o Qdrant.
- Montar prompts.
- Consultar o Ollama.
- Retornar respostas.

A API fica disponível em: text [http://localhost:8000](http://localhost:8000)

---

### Serviço `indexer`

Executa o indexador.
yaml indexer: build: ./indexer depends_on: - qdrant volumes: - /Users/vfosouza/Workspace:/repositories/Workspace - /Users/vfosouza/Workspace_Servier:/repositories/Workspace_Servier

Responsabilidades:

- Ler repositórios montados.
- Processar arquivos.
- Gerar embeddings.
- Armazenar informações no Qdrant.

---

## Configuração

As configurações estão separadas entre API e indexador.

---

### Configurações da API

Arquivo: text api/app/config.py

Principais variáveis:

| Variável | Descrição | Valor padrão |
|---|---|---|
| `OLLAMA_URL` | URL do serviço Ollama | `http://ollama:11434` |
| `OLLAMA_MODEL` | Modelo LLM utilizado | `qwen2.5:1.5b` |
| `QDRANT_HOST` | Host do Qdrant | `qdrant` |
| `QDRANT_PORT` | Porta do Qdrant | `6333` |
| `COLLECTION_NAME` | Nome da collection vetorial | `repositories` |
| `REFERENCE_PATTERNS` | Lista de termos para detectar busca por referência | Lista configurada |

---

### Configurações do Indexer

Arquivo: text indexer/app/config.py

Principais variáveis:

| Variável | Descrição | Valor padrão |
|---|---|---|
| `QDRANT_HOST` | Host do Qdrant | `qdrant` |
| `QDRANT_PORT` | Porta do Qdrant | `6333` |
| `COLLECTION_NAME` | Nome da collection | `repositories` |
| `CHUNK_SIZE` | Tamanho de cada chunk | `2000` |
| `CHUNK_OVERLAP` | Sobreposição entre chunks | `200` |
| `BATCH_SIZE` | Quantidade de itens por lote | `32` |
| `MAX_FILE_SIZE` | Tamanho máximo de arquivo indexável | `500000` |
| `SUPPORTED_EXTENSIONS` | Extensões aceitas | `.py`, `.sql`, `.yml`, etc. |
| `IGNORE_DIRS` | Diretórios ignorados | `.git`, `.venv`, `node_modules`, etc. |

---

## API

A API é construída com FastAPI.

### Health Check

Endpoint: 
http GET / json { "status": "running" }

Esse endpoint serve para validar se a API está ativa.

---

### Chat

O projeto possui uma rota de chat definida no módulo:
text api/app/routes/chat.py

Essa rota é responsável por receber perguntas e retornar respostas geradas pelo fluxo RAG.

Um exemplo esperado de payload pode seguir o formato abaixo, dependendo da implementação da rota:
json { "question": "Onde usei qdrant?" }

Resposta esperada: json { "answer": "..." }

---

## Indexer

O indexador é responsável por alimentar o Qdrant com dados pesquisáveis.

Ele realiza as seguintes etapas:

1. Percorre os diretórios montados.
2. Ignora diretórios configurados.
3. Filtra arquivos por extensão.
4. Ignora arquivos muito grandes.
5. Lê conteúdo textual.
6. Divide conteúdo em chunks.
7. Gera embeddings.
8. Salva vetores e metadados no Qdrant.

---

## Busca Semântica e Busca por Referência

O projeto possui dois modos principais de recuperação de contexto.

---

### Busca Semântica

A busca semântica usa embeddings para encontrar conteúdos semelhantes à pergunta.

Indicada para perguntas como:
text Explique o funcionamento do pipeline de dados.
text Como funciona o serviço de autenticação?
text Qual é a responsabilidade do indexador?

Características:

- Usa similaridade vetorial.
- Recupera os chunks mais próximos semanticamente.
- Retorna contexto para o LLM gerar uma resposta.
- Melhor para perguntas conceituais.

---

### Busca por Referência

A busca por referência usa termos explícitos da pergunta para localizar ocorrências nos arquivos indexados.

Indicada para perguntas como:
text Onde usei qdrant?
text Quem chama generate_embedding?
text Em qual arquivo aparece COLLECTION_NAME?
text Localize referências ao serviço rag.

Características:

- Percorre os documentos indexados no Qdrant.
- Busca termo em nome de arquivo e conteúdo.
- Agrupa resultados por arquivo.
- Extrai trechos próximos da ocorrência.
- Retorna contexto estruturado para o LLM.

---

## Modelo de Embeddings

O projeto utiliza o modelo:
text sentence-transformers/all-MiniLM-L6-v2

Esse modelo converte textos em vetores numéricos.

Vantagens:

- Leve.
- Rápido.
- Adequado para busca semântica.
- Bastante utilizado em aplicações RAG.

Cada arquivo indexado é dividido em chunks, e cada chunk recebe um embedding.  
Esses embeddings são armazenados no Qdrant para busca por similaridade.

---

## Banco Vetorial Qdrant

O Qdrant é utilizado para armazenar os embeddings dos documentos indexados.

Collection utilizada:
text repositories

Cada ponto armazenado no Qdrant representa um chunk de arquivo.

Um payload típico pode conter:
json { "file": "caminho/do/arquivo.py", "filename": "arquivo.py", "repository": "nome-do-repositorio", "content": "conteúdo do chunk" }

O Qdrant permite:

- Busca por similaridade vetorial.
- Armazenamento de metadados.
- Recuperação de contexto para RAG.
- Persistência local via volume Docker.

---

## Modelo LLM via Ollama

O projeto utiliza Ollama para executar localmente um modelo de linguagem.

Modelo configurado:
text qwen2.5:1.5b

O serviço `ollama-init` baixa automaticamente o modelo na inicialização do ambiente Docker.

O Ollama é acessado internamente pela API através da URL:
text [http://ollama:11434](http://ollama:11434)

---

## Como Executar o Projeto

### Pré-requisitos

É necessário ter instalado:

- Docker
- Docker Compose

Também é recomendado ter:

- Python
- Ambiente virtual configurado
- `uv`, caso deseje gerenciar dependências Python localmente

---

### Subir todos os serviços

Na raiz do projeto, execute:
bash docker compose up --build

Esse comando irá:

1. Construir a imagem da API.
2. Construir a imagem do indexador.
3. Subir o Qdrant.
4. Subir o Ollama.
5. Baixar o modelo `qwen2.5:1.5b`.
6. Inicializar a API.
7. Executar o indexer conforme configurado.

---

### Verificar se a API está rodando

Acesse:
text [http://localhost:8000](http://localhost:8000)

Ou execute:
bash curl [http://localhost:8000/](http://localhost:8000/)

Resposta esperada: json { "status": "running" }

---

## Como Indexar Repositórios

Os repositórios indexáveis são montados no serviço `indexer` através do `docker-compose.yaml`.

Exemplo:
yaml volumes:
- /Users/vfosouza/Workspace:/repositories/Workspace
- /Users/vfosouza/Workspace_Servier:/repositories/Workspace_Servier

Para indexar outros diretórios, altere os volumes:
yaml indexer: build: ./indexer depends_on: - qdrant volumes: - /caminho/local/do/repositorio:/repositories/repositorio

Depois execute novamente:
bash docker compose up --build indexer

Ou suba todos os serviços:
bash docker compose up --build

---

## Exemplos de Uso

### Pergunta conceitual
text Explique como funciona o serviço RAG deste projeto.
Fluxo utilizado:
text Busca semântica por embeddings
---

### Busca por referência
text Onde usei COLLECTION_NAME?

Fluxo utilizado:
text Busca por palavra-chave/referência

---

### Localizar uso de serviço
text Quem chama ask_llm?

Fluxo utilizado:
text Busca por referência

---

### Buscar arquivo
text Em qual arquivo aparece qdrant_repository?

Fluxo utilizado:
text Busca por referência

---

## Dependências

Dependências principais da API:
text fastapi uvicorn requests qdrant-client sentence-transformers

Descrição:

| Dependência | Uso |
|---|---|
| `fastapi` | Framework HTTP da API |
| `uvicorn` | Servidor ASGI |
| `requests` | Chamadas HTTP, especialmente para Ollama |
| `qdrant-client` | Comunicação com Qdrant |
| `sentence-transformers` | Geração de embeddings |

---

## Gerenciamento de Dependências

Este projeto utiliza ambiente Python e pode ser gerenciado com `uv`.

Exemplos úteis:

### Instalar dependências do projeto
bash uv sync
### Adicionar nova dependência
bash uv add nome-da-biblioteca
### Executar comandos Python no ambiente
bash uv run python arquivo.py

---

## Volumes Docker

O projeto define os seguintes volumes persistentes:
yaml volumes: ollama_data: qdrant_data:

### `ollama_data`

Armazena modelos baixados pelo Ollama.

Evita que o modelo precise ser baixado novamente a cada reinicialização.

### `qdrant_data`

Armazena os dados vetoriais indexados no Qdrant.

Permite manter a base indexada mesmo após recriar containers.

---

## Portas Utilizadas

| Serviço | Porta local | Porta interna | Descrição |
|---|---:|---:|---|
| API | `8000` | `8000` | FastAPI |
| Ollama | `11434` | `11434` | API do Ollama |
| Qdrant | `6333` | `6333` | API HTTP do Qdrant |

---

## Boas Práticas do Projeto

Algumas boas práticas já presentes ou recomendadas:

- Separação entre API e indexador.
- Uso de banco vetorial dedicado.
- Uso de Docker para facilitar execução.
- Separação de responsabilidades por módulos.
- Ignorar diretórios de dependências e build durante indexação.
- Limitar tamanho máximo de arquivos indexados.
- Dividir arquivos em chunks com overlap.
- Usar prompts específicos para tipos diferentes de pergunta.
- Evitar que o modelo invente respostas fora do contexto.

---

## Observações Importantes

### Sobre respostas do LLM

O modelo é instruído a responder com base apenas no contexto fornecido.  
Mesmo assim, como qualquer LLM, pode haver risco de imprecisão caso:

- o contexto recuperado seja insuficiente;
- o termo pesquisado não tenha sido indexado;
- os arquivos estejam desatualizados no Qdrant;
- a pergunta seja ambígua.

---

### Sobre atualização do índice

Sempre que os repositórios forem alterados, é necessário executar novamente o indexador para que o Qdrant reflita os arquivos atualizados.

---

### Sobre arquivos ignorados

Arquivos dentro de diretórios como `.git`, `.venv`, `node_modules`, `target`, `build` e `dist` não são indexados.

Isso é intencional para evitar:

- excesso de ruído;
- indexação de dependências externas;
- lentidão;
- consumo desnecessário de armazenamento vetorial.

---

### Sobre tamanho máximo de arquivo

Arquivos maiores que `MAX_FILE_SIZE` são ignorados.

Valor atual:
text 500000 bytes

Isso evita indexar arquivos muito grandes que poderiam prejudicar performance ou gerar chunks demais.

---

## Melhorias Futuras

Possíveis evoluções para o projeto:

- Criar endpoint específico para reindexação.
- Adicionar autenticação na API.
- Criar interface web para chat.
- Adicionar logs estruturados.
- Adicionar testes automatizados.
- Adicionar suporte a mais extensões.
- Melhorar ranking das buscas por referência.
- Adicionar cache de respostas.
- Adicionar suporte a múltiplas collections.
- Criar endpoint para listar repositórios indexados.
- Criar endpoint para consultar status do Qdrant.
- Criar endpoint para consultar modelos disponíveis no Ollama.
- Permitir configuração via variáveis de ambiente.
- Adicionar suporte a streaming de resposta do LLM.
- Adicionar métricas de tempo de resposta.
- Adicionar suporte a reranking dos chunks recuperados.
- Adicionar interface administrativa para limpar ou recriar collections.

---

## Resumo

O Personal Jarvis é uma solução local de assistente inteligente para consulta de repositórios e arquivos.  
Ele utiliza uma arquitetura RAG composta por:

- FastAPI para exposição HTTP.
- Indexer para processamento de arquivos.
- Sentence Transformers para embeddings.
- Qdrant para armazenamento vetorial.
- Ollama para geração de respostas com LLM local.

O projeto é adequado para auxiliar em análise de código, localização de referências, documentação técnica e entendimento de bases de código indexadas.