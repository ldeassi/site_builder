"""Quick script to diagnose Google Places pagination."""
import asyncio
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
load_dotenv(Path(__file__).resolve().parents[2] / "frontend" / ".env")

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY") or os.getenv("VITE_GOOGLE_MAPS_API_KEY")
URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"


async def test_pagination(use_referer: bool) -> None:
    headers = {"Referer": "http://127.0.0.1:5177/"} if use_referer else None
    async with httpx.AsyncClient(timeout=60) as client:
        r1 = await client.get(
            URL,
            params={
                "query": "businesses in Leesburg, VA, USA",
                "location": "39.1157,-77.5636",
                "radius": 25000,
                "key": API_KEY,
            },
            headers=headers,
        )
        d1 = r1.json()
        print(f"referer={use_referer} page1: {d1.get('status')} results={len(d1.get('results', []))}")
        token = d1.get("next_page_token")
        if not token:
            return
        await asyncio.sleep(2)
        r2 = await client.get(
            URL,
            params={"pagetoken": token, "key": API_KEY},
            headers=headers,
        )
        d2 = r2.json()
        print(
            f"referer={use_referer} page2: {d2.get('status')} "
            f"results={len(d2.get('results', []))} error={d2.get('error_message')}"
        )


async def main() -> None:
    if not API_KEY:
        raise SystemExit("No API key found")
    await test_pagination(False)
    await test_pagination(True)


if __name__ == "__main__":
    asyncio.run(main())
