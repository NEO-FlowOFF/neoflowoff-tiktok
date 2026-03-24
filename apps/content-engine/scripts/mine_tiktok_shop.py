#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import time
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests
from dotenv import load_dotenv
from openai import OpenAI
from tavily import TavilyClient

SCRIPT_PATH = Path(__file__).resolve()
MODULE_DIR = SCRIPT_PATH.parents[1]
REPO_ROOT = SCRIPT_PATH.parents[3]
DEFAULT_ENV_FILE = REPO_ROOT / ".env"
DEFAULT_OUTPUT_CSV = MODULE_DIR / "runtime" / "inputs" / "pending_products.csv"

DEFAULT_QUERIES = [
    "TikTok Shop Brasil produto viral casa e cozinha",
    "TikTok Shop Brasil beleza produto mais vendido",
    "TikTok Shop afiliado alta comissao produto tendencia",
]


def guess_image_url_from_result(url: str) -> str:
    clean = url.strip()
    if re.search(r"\.(png|jpe?g|webp)(\?.*)?$", clean, flags=re.I):
        return clean
    return ""


def fetch_tiktok_oembed_thumbnail(url: str) -> str:
    if "tiktok.com/" not in url:
        return ""
    oembed_url = f"https://www.tiktok.com/oembed?url={quote(url, safe='')}"
    try:
        response = requests.get(
            oembed_url,
            timeout=20,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        if response.status_code != 200:
            return ""
        payload = response.json()
        thumbnail = str(payload.get("thumbnail_url", "")).strip()
        return thumbnail
    except Exception:
        return ""


def resolve_image_url(source_url: str, cache: dict[str, str]) -> str:
    direct = guess_image_url_from_result(source_url)
    if direct:
        return direct
    cached = cache.get(source_url)
    if cached is not None:
        return cached
    thumb = fetch_tiktok_oembed_thumbnail(source_url)
    cache[source_url] = thumb
    return thumb


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pesquisa oportunidades e gera pending_products.csv para o pipeline neo_tiktokshop."
    )
    parser.add_argument("--env-file", default=str(DEFAULT_ENV_FILE))
    parser.add_argument("--output-csv", default=str(DEFAULT_OUTPUT_CSV))
    parser.add_argument("--max-results-per-query", type=int, default=None)
    parser.add_argument("--limit-products", type=int, default=None)
    parser.add_argument("--openai-model", default="")
    parser.add_argument("--skip-openai", action="store_true")
    parser.add_argument("--strict-openai", action="store_true")
    parser.add_argument("--query", action="append", default=[])
    return parser.parse_args()


def clean_name(title: str) -> str:
    candidate = re.split(r"[\-|:|•|/]", title)[0].strip()
    candidate = re.sub(
        r"\b(tiktok|shop|brasil|oficial|affiliate|afiliado)\b",
        "",
        candidate,
        flags=re.I,
    )
    candidate = re.sub(r"\s{2,}", " ", candidate).strip(" -:|/")
    return candidate[:90] if candidate else "Produto tendencia TikTok Shop"


def run_tavily_search(
    client: TavilyClient, queries: list[str], max_results_per_query: int
) -> list[dict[str, str]]:
    gathered: list[dict[str, str]] = []
    seen = set()
    for query in queries:
        response = client.search(
            query=query, search_depth="basic", max_results=max_results_per_query
        )
        for item in response.get("results", []):
            url = str(item.get("url", "")).strip()
            title = str(item.get("title", "")).strip()
            content = str(item.get("content", "")).strip()
            key = url or f"{query}:{title}"
            if not key or key in seen:
                continue
            seen.add(key)
            gathered.append(
                {
                    "query": query,
                    "url": url,
                    "title": title,
                    "content": content,
                }
            )
    return gathered


def llm_structured_products(
    rows: list[dict[str, str]],
    limit_products: int,
    model: str,
    skip_openai: bool,
    strict_openai: bool,
) -> tuple[list[dict[str, Any]], str]:
    image_cache: dict[str, str] = {}
    fallback_products = []
    for idx, row in enumerate(rows[:limit_products], start=1):
        name = clean_name(row["title"])
        fallback_products.append(
            {
                "name": name,
                "problem": "Demanda alta e decisao de compra impulsiva no feed",
                "offer": "Comissao competitiva para afiliado",
                "confidence": 0.45,
                "source_url": row["url"],
                "source_query": row["query"],
                "source_title": row["title"],
                "image_url": resolve_image_url(row["url"], image_cache),
            }
        )

    if skip_openai or not os.getenv("OPENAI_API_KEY"):
        return fallback_products, "fallback_no_openai"

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model_candidates = [model, "gpt-4o"]
    last_exc: Exception | None = None
    compact_rows = [
        {
            "query": r["query"],
            "url": r["url"],
            "title": r["title"][:180],
            "content": r["content"][:400],
        }
        for r in rows[:30]
    ]

    for model_name in model_candidates:
        try:
            response = client.chat.completions.create(
                model=model_name,
                response_format={"type": "json_object"},
                temperature=0.2,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Voce extrai oportunidades de produto para TikTok Shop a partir de snippets. "
                            "Retorne JSON estrito no formato {'products':[...]} com no maximo o limite pedido. "
                            "Campos por item: name, problem, offer, confidence (0 a 1), source_url, source_query, source_title, image_url."
                            "Quando nao houver image_url confiavel, retorne string vazia."
                        ),
                    },
                    {
                        "role": "user",
                        "content": json.dumps(
                            {
                                "limit_products": limit_products,
                                "rows": compact_rows,
                            },
                            ensure_ascii=False,
                        ),
                    },
                ],
            )
            payload = json.loads(response.choices[0].message.content)
            products = payload.get("products", [])
            normalized: list[dict[str, Any]] = []
            for item in products:
                source_url = str(item.get("source_url", "")).strip()
                normalized.append(
                    {
                        "name": str(item.get("name", "")).strip()[:120]
                        or "Produto tendencia TikTok Shop",
                        "problem": str(item.get("problem", "")).strip()[:220]
                        or "Demanda alta e decisao de compra impulsiva no feed",
                        "offer": str(item.get("offer", "")).strip()[:160]
                        or "Comissao competitiva para afiliado",
                        "confidence": float(item.get("confidence", 0.5)),
                        "source_url": source_url,
                        "source_query": str(item.get("source_query", "")).strip(),
                        "source_title": str(item.get("source_title", "")).strip(),
                        "image_url": str(item.get("image_url", "")).strip()
                        or resolve_image_url(source_url, image_cache),
                    }
                )
            if normalized:
                return normalized[:limit_products], f"openai_ok:{model_name}"
        except Exception as exc:
            last_exc = exc
            continue

    if strict_openai:
        raise RuntimeError(f"Falha OpenAI em modo estrito: {last_exc}") from last_exc
    return fallback_products, "fallback_openai_error"


def write_csv(products: list[dict[str, Any]], output_csv: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    now = int(time.time())
    with output_csv.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(
            fp,
            fieldnames=[
                "id",
                "name",
                "problem",
                "offer",
                "score",
                "source_url",
                "source_query",
                "source_title",
                "image_url",
            ],
        )
        writer.writeheader()
        for idx, product in enumerate(products, start=1):
            confidence = max(0.1, min(1.0, float(product.get("confidence", 0.5))))
            writer.writerow(
                {
                    "id": f"TXM_{now}_{idx}",
                    "name": product["name"],
                    "problem": product["problem"],
                    "offer": product["offer"],
                    "score": round(confidence * 10, 2),
                    "source_url": product.get("source_url", ""),
                    "source_query": product.get("source_query", ""),
                    "source_title": product.get("source_title", ""),
                    "image_url": product.get("image_url", ""),
                }
            )


def main() -> int:
    args = parse_args()
    load_dotenv(args.env_file, override=False)
    if args.max_results_per_query is None:
        args.max_results_per_query = int(
            os.getenv("NEO_MINE_MAX_RESULTS_PER_QUERY", "5")
        )
    if args.limit_products is None:
        args.limit_products = int(os.getenv("NEO_MINE_LIMIT_PRODUCTS", "8"))
    if not args.openai_model:
        args.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    tavily_key = os.getenv("TAVILY_API_KEY")
    if not tavily_key:
        print(json.dumps({"ok": False, "error": "TAVILY_API_KEY ausente"}))
        return 1

    queries = args.query if args.query else DEFAULT_QUERIES
    client = TavilyClient(api_key=tavily_key)
    rows = run_tavily_search(client, queries, args.max_results_per_query)
    if not rows:
        print(json.dumps({"ok": False, "error": "Sem resultados Tavily"}))
        return 1

    products, llm_status = llm_structured_products(
        rows=rows,
        limit_products=args.limit_products,
        model=args.openai_model,
        skip_openai=args.skip_openai,
        strict_openai=args.strict_openai,
    )

    if not products:
        print(json.dumps({"ok": False, "error": "Sem produtos estruturados"}))
        return 1

    output_csv = Path(args.output_csv).resolve()
    write_csv(products, output_csv)
    print(
        json.dumps(
            {
                "ok": True,
                "rows_researched": len(rows),
                "products": len(products),
                "llm_status": llm_status,
                "output_csv": str(output_csv),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
