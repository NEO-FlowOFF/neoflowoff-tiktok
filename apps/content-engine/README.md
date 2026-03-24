# Content Engine

Modulo isolado para pesquisa, geracao e publicacao de conteudo TikTok Shop.

## Fluxo

1. `mine_tiktok_shop.py`: pesquisa oportunidades e gera CSV de entrada.
2. `run_neo_tiktokshop.py`: gera roteiro, audio, video e publica no MinIO.
3. Imagem do video: prioriza `image_url` do CSV, tenta thumbnail via TikTok `oEmbed`, e so depois cai em geracao OpenAI (se habilitada).

## Comandos locais do modulo

```bash
make setup
make mine
make run
make auto
make research-auto
```

## Variaveis esperadas

Use `.env` na raiz do repositorio (ou passe `--env-file`):

- `OPENAI_API_KEY`
- `TAVILY_API_KEY`
- `OPENAI_MODEL`
- `NEO_GENERATE_IMAGE_IF_MISSING`
- `OPENAI_IMAGE_MODEL`
- `NEO_IMAGE_SIZE`
- `NEO_IMAGE_QUALITY`
- `NEO_MINE_MAX_RESULTS_PER_QUERY`
- `NEO_MINE_LIMIT_PRODUCTS`
- `NEO_RUN_MAX_PRODUCTS`
- `MINIO_ENDPOINT`
- `MINIO_PUBLIC_BASE_URL`
- `MINIO_ROOT_USER`
- `MINIO_ROOT_PASSWORD`
- `MINIO_BUCKET`

## Entradas e saidas

- Entrada CSV: `apps/content-engine/runtime/inputs/pending_products.csv`
- Saida video: `apps/content-engine/runtime/outputs/*_final_render.mp4`
- Saida metadata: `apps/content-engine/runtime/outputs/*_meta.json`
