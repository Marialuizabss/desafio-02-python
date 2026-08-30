# Sistema Inteligente de Processamento e Consulta de Atendimentos de Suporte

Projeto desenvolvido no Desafio 2 — Introdução a Python para IA do programa FIC_DEV.

## Equipe

- Maria Luiza Batista de Souza
- Yuri Lino Franco
- Adriano Froes da Costa

O projeto consiste na auditoria, correção e validação de um sistema gerado com apoio de Inteligência Artificial para processamento e consulta de atendimentos de suporte.

## Arquitetura

A aplicação é organizada em módulos com responsabilidades específicas para configuração, processamento de PDFs e OCR, validação e tratamento textual, persistência, análise de dados, geração de embeddings, armazenamento vetorial, RAG, API e interface web.

O fluxo principal da aplicação consiste em:

1. localizar e processar os documentos PDF;
2. realizar extração direta ou OCR conforme o tipo de página;
3. extrair, validar, normalizar e classificar os atendimentos;
4. persistir documentos, atendimentos, chunks e erros no SQLite;
5. complementar os registros com município e UF por meio de consulta de CEP;
6. gerar indicadores, arquivos de saída e gráficos;
7. gerar embeddings e armazenar os chunks no ChromaDB;
8. recuperar informações por busca semântica;
9. disponibilizar as consultas por linha de comando, FastAPI e Streamlit.

## Funcionalidades

- extração direta de PDFs com `pypdf`;
- processamento de páginas digitalizadas com Tesseract;
- extração de campos com expressões regulares;
- normalização, validação, classificação e deduplicação;
- persistência com SQLite e SQLAlchemy;
- consulta, atualização e exclusão controlada de atendimentos;
- consulta de CEP para obtenção de município e UF;
- limpeza textual, tokenização, stopwords e lematização leve;
- análise de dados com Pandas e NumPy;
- exportação dos dados tratados em CSV;
- geração de indicadores em JSON;
- geração de gráficos em PNG;
- criação de chunks com metadados rastreáveis;
- embeddings locais com `sentence-transformers`;
- armazenamento vetorial persistente com ChromaDB;
- busca semântica com filtros por categoria e protocolo;
- recuperação local e RAG opcional com LangChain/OpenAI;
- API REST com FastAPI;
- interface web com Streamlit;
- testes automatizados com Pytest.

## Preparação

Crie e ative o ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

Crie o arquivo de variáveis de ambiente:

```bash
cp .env.example .env
```

No Ubuntu ou GitHub Codespaces, instale também Poppler e Tesseract:

```bash
sudo apt update
sudo apt install poppler-utils tesseract-ocr tesseract-ocr-por
```

## Variáveis de ambiente

As configurações sensíveis são carregadas por variáveis de ambiente.

O arquivo `.env.example` apresenta as variáveis esperadas pelo projeto. A chave da OpenAI deve ser configurada somente quando o modo RAG com geração de resposta for utilizado.

Exemplo:

```env
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
APP_ENV=development
```

O arquivo `.env` não deve ser versionado.

## Execução

### Pipeline

```bash
python -m src.main
```

### Pipeline com indexação vetorial

```bash
python -m src.main --indexar
```

### Consulta por linha de comando

```bash
python -m src.main --pergunta "Quais problemas mencionam instalação do Python?"
```

### FastAPI

```bash
uvicorn src.api:app --reload
```

Após iniciar a API, a documentação interativa pode ser acessada pelo endpoint `/docs`.

### Streamlit

```bash
streamlit run src/app_streamlit.py
```

### Testes

```bash
python -m pytest -q
```

## Decisões de validação e deduplicação

Os registros são analisados e classificados como válidos, incompletos, inválidos ou duplicados de acordo com os campos encontrados e as regras de validação.

São verificadas informações como protocolo, data, e-mail, CEP e tempo de atendimento.

Os motivos das classificações são preservados para permitir auditoria dos registros.

O protocolo é utilizado para identificação de duplicidades. Registros repetidos são classificados como duplicados e não são reinseridos como novos atendimentos no banco.

## Processamento textual

O texto original dos atendimentos é preservado para manter a rastreabilidade dos dados.

A versão utilizada no processamento textual passa por:

- normalização de espaços;
- conversão para minúsculas;
- remoção de acentos com `unicodedata`;
- tokenização utilizando expressões regulares;
- remoção de stopwords;
- redução morfológica simplificada por sufixos por meio da função `lemma_light`.

Foi utilizada uma estratégia de lematização leve para evitar a necessidade de modelos linguísticos externos de maior porte.

## Chunking

Os textos são divididos em chunks de aproximadamente 500 caracteres, com sobreposição de 80 caracteres.

A divisão procura utilizar espaços como limites quando possível, evitando cortes desnecessários no meio das palavras.

Cada chunk mantém metadados que permitem rastrear sua origem, incluindo documento, página, protocolo e categoria.

## Persistência

O sistema utiliza SQLite e SQLAlchemy para persistência.

As principais entidades são:

- `Documento`;
- `Atendimento`;
- `Chunk`;
- `ErroProcessamento`.

As operações de banco são executadas por meio de sessões e transações controladas.

O sistema disponibiliza operações de inserção, consulta, atualização e exclusão de atendimentos e possui restrição de unicidade para impedir duplicidade de protocolo.

Em caso de falha durante o OCR, o documento não é marcado como completamente processado, permitindo uma nova tentativa em execução posterior.

## Consulta de CEP

Quando um atendimento possui CEP disponível, o pipeline consulta uma API pública para complementar os dados com município e UF.

A integração utiliza timeout e tratamento de falhas. CEPs inexistentes ou indisponibilidade do serviço externo não interrompem o processamento dos demais registros.

## Indicadores e visualizações

O sistema gera indicadores relacionados aos documentos e atendimentos processados, incluindo:

- total de documentos e páginas;
- quantidade e percentual por classificação;
- quantidade por categoria e status;
- quantidade por município e UF;
- média, mediana e desvio-padrão do tempo de atendimento;
- categoria com maior volume;
- categoria com maior tempo médio;
- percentual de páginas processadas por OCR;
- erros por tipo e por etapa;
- método de extração.

Também são gerados arquivos CSV, JSON, log de processamento e gráficos em PNG.

Nos gráficos, registros sem status são apresentados como `Sem informação`, preservando os dados originais e evitando categorias visuais sem identificação.

## Busca semântica

Os chunks são convertidos em embeddings locais utilizando `sentence-transformers`.

Os vetores e metadados são armazenados em uma coleção persistente do ChromaDB.

A consulta semântica retorna os trechos mais semelhantes à pergunta e permite controlar a quantidade de resultados por `top_k`, além de aplicar filtros por categoria ou protocolo.

## RAG e modo sem chave da OpenAI

O sistema pode funcionar sem uma chave da OpenAI.

Sem `OPENAI_API_KEY`, é utilizado o modo de recuperação local, no qual os chunks mais semelhantes e suas fontes são apresentados sem realizar chamada a um modelo de linguagem.

Quando uma chave está configurada, o projeto utiliza LangChain e o modelo definido em `OPENAI_MODEL` para construir uma resposta baseada no contexto recuperado.

A cadeia orienta o modelo a responder somente com informações sustentadas pelo contexto e a indicar as fontes utilizadas.

Caso a chamada ao modelo apresente erro, o sistema retorna ao modo de recuperação local em vez de interromper a consulta.

## Tratamento de erros

Falhas isoladas não devem interromper todo o processamento.

Erros relevantes são registrados no banco e/ou no arquivo de log para permitir diagnóstico posterior.

Entre os cenários tratados estão falhas de OCR, registros duplicados, dados inválidos, indisponibilidade da API de CEP e falhas relacionadas à utilização do modelo de linguagem.

## Limitações conhecidas

- a lematização utilizada é uma redução morfológica simplificada e não substitui um analisador linguístico completo;
- a extração por expressões regulares foi desenvolvida considerando o formato dos documentos fornecidos no desafio;
- mudanças significativas no layout dos documentos podem exigir novos padrões de extração;
- a suíte de testes automatizados não cobre todos os componentes do sistema, sendo complementada por testes manuais e de integração realizados durante a auditoria;
- a integração com OpenAI/LangChain está implementada, porém a execução utilizando a API oficial da OpenAI não foi validada durante a auditoria por indisponibilidade de créditos.

## Uso de ferramentas de IA

Ferramentas de Inteligência Artificial foram utilizadas como apoio durante a auditoria, investigação e correção do projeto.

A IA foi utilizada principalmente para:

- análise e compreensão do código existente;
- investigação de erros encontrados durante a execução;
- auxílio na identificação das possíveis causas dos defeitos;
- sugestões de alterações no código;
- elaboração e revisão de testes manuais;
- apoio na organização da documentação técnica.

As sugestões geradas por IA não foram consideradas automaticamente corretas. Algumas precisaram ser adaptadas após a execução do sistema e outras não foram adotadas quando apresentavam risco de alterar funcionalidades que já estavam validadas.

As alterações aceitas foram verificadas por meio da execução do sistema, testes automatizados e testes manuais.

A equipe permaneceu responsável pela compreensão, revisão, execução e validação do código entregue.