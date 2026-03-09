# Julia JTT TikTok Stack

Monorepo preparado para Railway com:

- `@neomello/db`: Prisma 7, cofre de estado e criptografia simetrica para tokens OAuth.
- `@neomello/tiktok-sdk`: cliente de posting TikTok com validacao de payload.
- `@neomello/api`: OAuth callback, authorize URL e webhook ingress idempotente.
- `@neomello/worker`: BullMQ, refresh de token, projector da inbox e push de inventario.

## Servicos Railway

### Infra

- PostgreSQL Railway para `DATABASE_URL`
- Redis Railway para `REDIS_URL`

### API

- Root Directory: repositorio raiz
- Build Command: `npm run db:generate && npm run build`
- Start Command: `npm run start --workspace @neomello/api`

### Worker

- Root Directory: repositorio raiz
- Build Command: `npm run db:generate && npm run build`
- Start Command: `npm run start --workspace @neomello/worker`

### Cron

- nao precisa de servico separado
- o proprio worker agenda o scan de refresh e inbox com BullMQ Job Scheduler
- Schedule sugerido: `*/5 * * * *`

## Variaveis de ambiente

### Compartilhadas

- `DATABASE_URL`
- `REDIS_URL`
- `TOKEN_ENCRYPTION_KEY`

### API

- `PORT`
- `API_BASE_URL`
- `TIKTOK_SHOP_APP_KEY`
- `TIKTOK_SHOP_APP_SECRET`
- `TIKTOK_SHOP_AUTHORIZE_URL`
- `TIKTOK_SHOP_TOKEN_URL`
- `TIKTOK_SHOP_REDIRECT_URI`
- `OAUTH_STATE_SECRET`
- `TIKTOK_WEBHOOK_SIGNATURE_HEADER`
- `TIKTOK_WEBHOOK_TIMESTAMP_HEADER`
- `TIKTOK_WEBHOOK_SECRET`

### Worker

- `TIKTOK_SHOP_API_BASE_URL`
- `TIKTOK_SHOP_TOKEN_URL`
- `TIKTOK_SHOP_APP_KEY`
- `TIKTOK_SHOP_APP_SECRET`
- `TIKTOK_SHOP_AUTH_REVOKED_EVENT`
- `TIKTOK_SHOP_INVENTORY_UPDATE_PATH`

## Fluxo

1. `GET /oauth/tiktok-shop/authorize` gera URL autorizacao com `state` assinado.
2. `GET /oauth/tiktok-shop/callback` troca `code` por tokens e grava `SocialAccount`.
3. `POST /webhooks/tiktok-shop` valida assinatura e grava `WebhookEventInbox`.
4. `cron` enfileira refresh de token e eventos pendentes.
5. `worker` processa filas com kill switch por `status = ACTIVE` e agenda scans recorrentes de refresh/webhook.
