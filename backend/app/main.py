from urllib.parse import quote

import httpx
from fastapi import FastAPI, HTTPException

from .config import settings

app = FastAPI(title="Oráculo")

BASE_URL = "https://api.clashroyale.com/v1"


async def supercell_get(path: str):
    if not settings.cr_api_key:
        raise HTTPException(500, "Falta CR_API_KEY en el .env")

    headers = {"Authorization": f"Bearer {settings.cr_api_key}"}
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{BASE_URL}{path}", headers=headers)

    if r.status_code != 200:
        raise HTTPException(r.status_code, r.text)
    return r.json()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/cards")
async def cards():
    return await supercell_get("/cards")


@app.get("/players/{tag}/battlelog")
async def battlelog(tag: str):
    # los tags llevan '#', que en la URL debe ir como %23
    clean = quote("#" + tag.lstrip("#"), safe="")
    return await supercell_get(f"/players/{clean}/battlelog")