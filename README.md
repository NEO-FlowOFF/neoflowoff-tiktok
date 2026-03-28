# neoflowoff-tiktok

Control Plane do ecossistema modular TikTok Shop da NEO FlowOFF.

Este repositorio nao e API de produto.
Este repositorio nao e worker de produto.
Este repositorio coordena, documenta e orquestra os modulos soberanos.

## Leitura rapida

Arquitetura ativa:

- `neo-content-landing`
- `neo-content-dashboard`
- `neo-content-accounts`
- `neo-content-engine`

Estado atual:

- `neo-content-landing` vive em `../neo-content-landing`
- `neo-content-dashboard` vive em `../neo-content-dashboard`
- `neo-content-accounts` vive em `../neo-content-accounts`
- `neo-content-engine` vive em `../neo-content-engine`
- `neoflowoff-tiktok` e o Control Plane dessa topologia

## Fronteiras de dominio

### 1) neo-content-landing

Responsabilidade:

- site publico
- superficie de entrada

Fonte de verdade:

- `../neo-content-landing`
- remoto: [NEO-FlowOFF/neo-content-landing](https://github.com/NEO-FlowOFF/neo-content-landing)

### 2) neo-content-dashboard

Responsabilidade:

- painel operacional
- consumo da API de contas

Fonte de verdade:

- `../neo-content-dashboard`
- remoto: [NEO-FlowOFF/neo-content-dashboard](https://github.com/NEO-FlowOFF/neo-content-dashboard)

### 3) neo-content-accounts

Responsabilidade:

- API OAuth TikTok Shop
- webhooks
- persistencia em Postgres
- filas e jobs (worker)
- SDK TikTok

Fonte de verdade:

- `../neo-content-accounts`
- remoto: [NEO-FlowOFF/neo-content-accounts](https://github.com/NEO-FlowOFF/neo-content-accounts)

### 4) neo-content-engine

Responsabilidade:

- pesquisa de oportunidades
- geracao de roteiro, audio e video
- pipeline local-first
- uso de OpenAI para conteudo

Fonte de verdade:

- `../neo-content-engine`
- remoto: [NEO-FlowOFF/neo-content-engine](https://github.com/NEO-FlowOFF/neo-content-engine)

## Como operar este repositorio

Este repositorio serve para:

- governanca tecnica
- documentacao
- auditoria
- atalhos de orquestracao

Este repositorio nao deve receber codigo de produto novo.

## Railway

Leitura correta no Railway:

- Projeto stack de contas: `neo-content-accounts-stack`
- API e Worker apontam para o repo `neo-content-accounts`
- `Postgres` e `Redis` suportam `neo-content-accounts`

Mapeamento alvo:

- `landing` -> `neo-content-landing`
- `dashboard` -> `neo-content-dashboard`
- `neo-content-api` (ou nome de servico equivalente no painel) -> `neo-content-accounts`
- `neo-content-worker` -> `neo-content-accounts`

## Variaveis operacionais

A raiz `neoflowoff-tiktok` nao e fonte primaria de `.env` de producao.

Variaveis devem viver por modulo:

- `../neo-content-accounts/.env`
- `../neo-content-dashboard/.env`
- `../neo-content-landing/.env`
- `../neo-content-engine/.env`

## Documentos de apoio

- [SETUP.md](./SETUP.md)
- [MODULAR_ARCHITECTURE.md](./MODULAR_ARCHITECTURE.md)
- [RAILWAY_WORKSPACE.md](./RAILWAY_WORKSPACE.md)
- [NEXTSTEPS.md](./NEXTSTEPS.md)

## Regra de ouro

Se a mudanca for de produto, codigo, deploy, integracao ou dado, edite no repositorio soberano.
Use este repositorio para coordenacao do ecossistema.
