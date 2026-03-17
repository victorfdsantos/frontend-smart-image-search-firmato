import httpx
import os
from typing import Optional

API_BASE   = os.getenv("API_BASE",   "http://firmato-api:8000")
API_PUBLIC = os.getenv("API_PUBLIC", "")


async def get_products(page: int = 1, page_size: int = 20, active_filters: dict = None) -> dict:
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            params = {"page": page, "page_size": page_size}
            if active_filters:
                for k, values in active_filters.items():
                    if values:
                        params[k] = ",".join(values)
            resp = await client.get(
                f"{API_BASE}/products",
                params=params,
            )
            resp.raise_for_status()
            return resp.json()
    except Exception:
        return {"page": page, "page_size": page_size, "total": 0, "total_pages": 1, "items": []}


async def get_product_detail(product_id: str) -> Optional[dict]:
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{API_BASE}/products/{product_id}")
            resp.raise_for_status()
            return resp.json()
    except Exception:
        return None


def image_url(product_id: int) -> str:
    return f"{API_PUBLIC}/api/static/images/{product_id}.jpg"


async def get_filter_options(active_filters: dict = None) -> dict:
    try:
        params = {}
        if active_filters:
            for k, values in active_filters.items():
                if values:
                    params[k] = ",".join(values)
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{API_BASE}/filters/options", params=params)
            resp.raise_for_status()
            return resp.json()
    except Exception:
        return {"fields": [], "labels": {}, "options": {}, "active_filters": {}}


async def search_products(
    query: str = None,
    image_bytes: bytes = None,
    top_k: int = 20,
    active_filters: dict = None,
) -> dict:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            params = {"top_k": top_k}
            if query:
                params["q"] = query
            if active_filters:
                for k, values in active_filters.items():
                    if values:
                        params[k] = ",".join(values)

            files = {"image": ("image.jpg", image_bytes, "image/jpeg")} if image_bytes else None

            resp = await client.post(
                f"{API_BASE}/search",
                params=params,
                files=files,
            )
            resp.raise_for_status()
            return resp.json()
    except Exception:
        return {"total": 0, "items": []}