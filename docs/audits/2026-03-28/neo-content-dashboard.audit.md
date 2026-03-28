# Audit Report - neo-content-dashboard

- Project path: `/Users/nettomello/CODIGOS/neo-content-dashboard`
- Audit date: `2026-03-28`
- Auditoria: somente leitura e validação operacional

## 1. Snapshot

- Git: repository válido
- Branch: `main`
- Working tree: limpa (sem mudanças rastreadas)
- Último commit: `fc78f4a` em `2026-03-24 18:05:22 -0300`

## 2. Checks executados

- `pnpm exec tsc --noEmit` -> **OK**
- `pnpm run build` -> **FALHA esperada sem env de build**
  - erro: `VITE_API_BASE_URL is required to build the dashboard`
  - origem: `vite.config.ts` linha de guarda de build

## 3. Higiene de segurança e estrutura

- `.env` não rastreado e ignorado corretamente
- `.env.example` rastreado
- `dist` e `node_modules` ignorados
- Sem sinais de segredo rastreado nesta auditoria

## 4. Achados

### Alto

- Nenhum.

### Médio

- Build de produção depende obrigatoriamente de `VITE_API_BASE_URL`.
- Sem esse valor no ambiente, o build falha por design.

### Baixo

- Tamanho local (`140M`) em linha com artefatos de frontend local.

## 5. Veredito

**Saudável com pré-condição de ambiente.** O módulo está correto, mas o build exige variável explícita.

## 6. Ação recomendada

- Garantir `VITE_API_BASE_URL` em CI/CD e ambiente local de release.
- Para auditoria técnica rápida, usar `pnpm exec tsc --noEmit` quando não houver env de release.
