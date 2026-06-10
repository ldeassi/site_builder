"""
Google Places business discovery with paginated search.

Uses Places API (New) when available; falls back to legacy Text Search + Details.
Server-side calls avoid browser CORS/referrer issues that cause 403 from the frontend.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any, Literal
from urllib.parse import quote

import httpx

logger = logging.getLogger(__name__)

SEARCH_RADIUS_METERS = 25_000
PAGE_SIZE = 20
NEW_API_URL = "https://places.googleapis.com/v1/places:searchText"
LEGACY_TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
LEGACY_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"

NEW_FIELD_MASK = ",".join(
    [
        "places.id",
        "places.displayName",
        "places.formattedAddress",
        "places.websiteUri",
        "places.nationalPhoneNumber",
        "places.internationalPhoneNumber",
        "places.rating",
        "places.userRatingCount",
        "places.primaryType",
        "places.types",
        "nextPageToken",
    ]
)

PlacesProvider = Literal["new", "legacy"]

BULK_SEARCH_CATEGORIES = [
    "businesses",
    "restaurants",
    "shops",
    "stores",
    "services",
    "contractors",
    "salons",
    "barbers",
    "dentists",
    "doctors",
    "lawyers",
    "hotels",
    "gyms",
    "cafes",
    "auto repair",
    "plumbers",
    "electricians",
    "real estate",
    "insurance",
    "banks",
    "churches",
    "schools",
    "veterinarians",
    "pharmacies",
    "cleaning services",
]

MAX_BULK_RESULTS = 500
BULK_QUERY_DELAY_SEC = 0.25
RAW_LEGACY_LOG_SAMPLE_SIZE = 5


def _format_category(primary_type: str | None, types: list[str] | None) -> str:
    raw = primary_type
    if not raw and types:
        raw = next(
            (t for t in types if t not in ("point_of_interest", "establishment")),
            types[0] if types else None,
        )
    if not raw:
        return "Business"
    return re.sub(r"\b\w", lambda m: m.group(0).upper(), raw.replace("_", " "))


def _normalize_place_id(place_id: str | None) -> str:
    if not place_id:
        return ""
    return place_id[7:] if place_id.startswith("places/") else place_id


def _display_name(value: Any) -> str:
    if not value:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return str(value.get("text") or "")
    return str(value)


def _business_dict(
    *,
    place_id: str,
    name: str,
    address: str,
    category: str,
    rating: float | None,
    review_count: int | None,
    website_url: str | None,
    phone: str | None,
) -> dict[str, Any]:
    website = (website_url or "").strip() or None
    return {
        "placeId": place_id,
        "name": name,
        "address": address,
        "category": category,
        "rating": rating,
        "reviewCount": review_count,
        "mapsUrl": (
            "https://www.google.com/maps/search/?api=1"
            f"&query={quote(name)}&query_place_id={place_id}"
        ),
        "hasWebsite": bool(website),
        "websiteUrl": website,
        "phone": phone,
        "email": None,
    }


def _place_from_new_api(place: dict[str, Any]) -> dict[str, Any] | None:
    place_id = _normalize_place_id(place.get("id"))
    name = _display_name(place.get("displayName"))
    if not place_id or not name:
        return None
    website = (place.get("websiteUri") or "").strip() or None
    phone = place.get("nationalPhoneNumber") or place.get("internationalPhoneNumber")
    return _business_dict(
        place_id=place_id,
        name=name,
        address=place.get("formattedAddress") or "",
        category=_format_category(place.get("primaryType"), place.get("types")),
        rating=place.get("rating"),
        review_count=place.get("userRatingCount"),
        website_url=website,
        phone=phone,
    )


async def _search_new_api(
    client: httpx.AsyncClient,
    api_key: str,
    query: str,
    lat: float,
    lng: float,
    page_token: str | None,
    referer: str | None = None,
) -> tuple[list[dict[str, Any]], str | None, int]:
    body: dict[str, Any] = {
        "textQuery": query,
        "pageSize": PAGE_SIZE,
        "locationBias": {
            "circle": {
                "center": {"latitude": lat, "longitude": lng},
                "radius": SEARCH_RADIUS_METERS,
            }
        },
    }
    if page_token:
        body["pageToken"] = page_token

    response = await client.post(
        NEW_API_URL,
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": NEW_FIELD_MASK,
            **({"Referer": referer} if referer else {}),
        },
        json=body,
        timeout=30.0,
    )
    data = response.json() if response.content else {}

    if response.status_code != 200:
        message = (data.get("error") or {}).get("message") or f"HTTP {response.status_code}"
        raise RuntimeError(message)

    raw_places = data.get("places") or []
    businesses = [b for p in raw_places if (b := _place_from_new_api(p))]
    next_token = data.get("nextPageToken")
    return businesses, next_token, len(raw_places)


async def _legacy_place_details(
    client: httpx.AsyncClient,
    api_key: str,
    place_id: str,
    referer: str | None = None,
) -> tuple[str | None, str | None]:
    response = await client.get(
        LEGACY_DETAILS_URL,
        params={
            "place_id": place_id,
            "fields": "website,formatted_phone_number,international_phone_number",
            "key": api_key,
        },
        headers={"Referer": referer} if referer else None,
        timeout=20.0,
    )
    data = response.json() if response.content else {}
    if data.get("status") != "OK":
        return None, None
    result = data.get("result") or {}
    website = (result.get("website") or "").strip() or None
    phone = result.get("formatted_phone_number") or result.get("international_phone_number")
    return website, phone


async def _legacy_place_details_raw(
    client: httpx.AsyncClient,
    api_key: str,
    place_id: str,
    referer: str | None = None,
) -> dict[str, Any]:
    response = await client.get(
        LEGACY_DETAILS_URL,
        params={
            "place_id": place_id,
            "fields": "website,formatted_phone_number,international_phone_number",
            "key": api_key,
        },
        headers={"Referer": referer} if referer else None,
        timeout=20.0,
    )
    return response.json() if response.content else {}


async def fetch_legacy_raw_sample(
    *,
    api_key: str,
    query: str,
    lat: float,
    lng: float,
    referer: str | None = None,
    sample_size: int = RAW_LEGACY_LOG_SAMPLE_SIZE,
) -> list[Any]:
    """
    Fetch raw Google Legacy JSON for text search + place details (first N results).
    Does not transform results — for debug logging only.
    """
    logs: list[Any] = []
    async with httpx.AsyncClient() as client:
        response = await client.get(
            LEGACY_TEXT_SEARCH_URL,
            params={
                "query": query,
                "location": f"{lat},{lng}",
                "radius": SEARCH_RADIUS_METERS,
                "key": api_key,
            },
            headers={"Referer": referer} if referer else None,
            timeout=30.0,
        )
        data = response.json() if response.content else {}
        status = data.get("status")
        raw_results = data.get("results") or []
        sample = raw_results[:sample_size]

        text_search_log = {
            "api": "legacy_textsearch",
            "url": LEGACY_TEXT_SEARCH_URL,
            "request": {
                "query": query,
                "location": f"{lat},{lng}",
                "radius": SEARCH_RADIUS_METERS,
            },
            "status": status,
            "error_message": data.get("error_message"),
            "results_count": len(raw_results),
            "results": sample,
        }
        logs.append(text_search_log)
        logger.info(
            "RAW Google Legacy textsearch (first %d): %s",
            len(sample),
            json.dumps(text_search_log, default=str),
        )

        if status not in ("OK", "ZERO_RESULTS"):
            return logs

        for raw in sample:
            place_id = raw.get("place_id")
            if not place_id:
                continue
            details_log = {
                "api": "legacy_details",
                "url": LEGACY_DETAILS_URL,
                "place_id": place_id,
                "response": await _legacy_place_details_raw(client, api_key, place_id, referer),
            }
            logs.append(details_log)
            logger.info(
                "RAW Google Legacy details place_id=%s: %s",
                place_id,
                json.dumps(details_log["response"], default=str),
            )

    return logs


async def _search_legacy_api(
    client: httpx.AsyncClient,
    api_key: str,
    query: str,
    lat: float,
    lng: float,
    page_token: str | None,
    referer: str | None = None,
    capture_raw_sample: int = 0,
) -> tuple[list[dict[str, Any]], str | None, int, list[Any]]:
    params: dict[str, Any] = {"key": api_key}
    if page_token:
        # Google requires a short delay before a pagetoken request is valid.
        await asyncio.sleep(2.0)
        params["pagetoken"] = page_token
    else:
        params["query"] = query
        params["location"] = f"{lat},{lng}"
        params["radius"] = SEARCH_RADIUS_METERS

    response = await client.get(
        LEGACY_TEXT_SEARCH_URL,
        params=params,
        headers={"Referer": referer} if referer else None,
        timeout=30.0,
    )
    data = response.json() if response.content else {}
    status = data.get("status")

    if status not in ("OK", "ZERO_RESULTS"):
        message = data.get("error_message") or status or "Legacy Places search failed"
        raise RuntimeError(message)

    raw_results = data.get("results") or []
    next_token = data.get("next_page_token")

    raw_google_logs: list[Any] = []
    if capture_raw_sample > 0 and not page_token:
        sample = raw_results[:capture_raw_sample]
        text_search_log = {
            "api": "legacy_textsearch",
            "url": LEGACY_TEXT_SEARCH_URL,
            "request": {
                "query": query,
                "location": f"{lat},{lng}",
                "radius": SEARCH_RADIUS_METERS,
            },
            "status": status,
            "error_message": data.get("error_message"),
            "results_count": len(raw_results),
            "results": sample,
        }
        raw_google_logs.append(text_search_log)
        logger.info(
            "RAW Google Legacy textsearch (first %d): %s",
            len(sample),
            json.dumps(text_search_log, default=str),
        )
        for raw in sample:
            place_id = raw.get("place_id")
            if not place_id:
                continue
            details_log = {
                "api": "legacy_details",
                "url": LEGACY_DETAILS_URL,
                "place_id": place_id,
                "response": await _legacy_place_details_raw(client, api_key, place_id, referer),
            }
            raw_google_logs.append(details_log)
            logger.info(
                "RAW Google Legacy details place_id=%s: %s",
                place_id,
                json.dumps(details_log["response"], default=str),
            )

    sem = asyncio.Semaphore(5)

    async def enrich(raw: dict[str, Any]) -> dict[str, Any] | None:
        place_id = raw.get("place_id")
        name = raw.get("name")
        if not place_id or not name:
            return None
        async with sem:
            website, phone = await _legacy_place_details(client, api_key, place_id, referer)
        return _business_dict(
            place_id=place_id,
            name=name,
            address=raw.get("formatted_address") or raw.get("vicinity") or "",
            category=_format_category(None, raw.get("types")),
            rating=raw.get("rating"),
            review_count=raw.get("user_rating_total"),
            website_url=website,
            phone=phone,
        )

    enriched = await asyncio.gather(*(enrich(r) for r in raw_results))
    businesses = [b for b in enriched if b]
    return businesses, next_token, len(raw_results), raw_google_logs


async def search_businesses_page(
    *,
    api_key: str,
    query: str,
    lat: float,
    lng: float,
    page_token: str | None = None,
    provider: PlacesProvider | None = None,
    referer: str | None = None,
    capture_raw_sample: int = 0,
) -> dict[str, Any]:
    """
    Fetch one page (~20) of businesses near a location.

    Returns businesses, next page token, provider used, and a debug line.
    """
    if not api_key:
        raise ValueError("Google Maps API key is required")

    async with httpx.AsyncClient() as client:
        active_provider = provider
        page_num_hint = "next" if page_token else "1"

        if active_provider in (None, "new"):
            try:
                businesses, next_token, raw_count = await _search_new_api(
                    client, api_key, query, lat, lng, page_token, referer
                )
                return {
                    "businesses": businesses,
                    "nextPageToken": next_token,
                    "hasNextPage": bool(next_token),
                    "rawCount": raw_count,
                    "provider": "new",
                    "debugLine": (
                        f"Places API (New) page {page_num_hint}: "
                        f"{raw_count} from Google, hasNext={bool(next_token)}"
                    ),
                }
            except Exception as exc:
                if active_provider == "new":
                    raise
                logger.warning("Places API (New) unavailable, using legacy Text Search: %s", exc)
                if page_token:
                    raise RuntimeError(
                        "Pagination token expired. Start a new search — "
                        "enable Places API (New) in Google Cloud for reliable paging."
                    ) from exc
                active_provider = "legacy"

        businesses, next_token, raw_count, raw_google_logs = await _search_legacy_api(
            client, api_key, query, lat, lng, page_token, referer, capture_raw_sample
        )
        return {
            "businesses": businesses,
            "nextPageToken": next_token,
            "hasNextPage": bool(next_token),
            "rawCount": raw_count,
            "provider": "legacy",
            "rawGoogleLogs": raw_google_logs,
            "debugLine": (
                f"Legacy Places API page {page_num_hint}: "
                f"{raw_count} from Google, hasNext={bool(next_token)}"
            ),
        }


async def search_businesses_bulk(
    *,
    api_key: str,
    location_name: str,
    lat: float,
    lng: float,
    referer: str | None = None,
    max_results: int = MAX_BULK_RESULTS,
) -> dict[str, Any]:
    """
    Aggregate up to max_results unique businesses using multiple category queries.
    Uses one API page (~20) per category to avoid unreliable legacy pagetokens.
    """
    seen: set[str] = set()
    businesses: list[dict[str, Any]] = []
    debug_lines: list[str] = []
    errors: list[str] = []
    provider: PlacesProvider | None = None

    sample_query = f"businesses in {location_name}"
    try:
        raw_google_logs = await fetch_legacy_raw_sample(
            api_key=api_key,
            query=sample_query,
            lat=lat,
            lng=lng,
            referer=referer,
        )
    except Exception as exc:
        logger.warning("Legacy raw sample capture failed: %s", exc)
        raw_google_logs = []

    for category in BULK_SEARCH_CATEGORIES:
        if len(businesses) >= max_results:
            break

        query = f"{category} in {location_name}"
        try:
            page = await search_businesses_page(
                api_key=api_key,
                query=query,
                lat=lat,
                lng=lng,
                page_token=None,
                provider=provider,
                referer=referer,
            )
            provider = page["provider"]

            added = 0
            for biz in page["businesses"]:
                pid = biz.get("placeId")
                if not pid or pid in seen:
                    continue
                seen.add(pid)
                businesses.append(biz)
                added += 1
                if len(businesses) >= max_results:
                    break

            debug_lines.append(
                f'"{category}": {page["rawCount"]} raw, +{added} new (total {len(businesses)})'
            )
        except Exception as exc:
            msg = f'"{category}": {exc}'
            errors.append(msg)
            logger.warning("Bulk search query failed: %s", msg)

        await asyncio.sleep(BULK_QUERY_DELAY_SEC)

    debug_lines.append(f"Done: {len(businesses)} unique businesses (max {max_results})")

    return {
        "businesses": businesses,
        "debugLines": debug_lines,
        "errors": errors,
        "provider": provider or "legacy",
        "rawGoogleLogs": raw_google_logs,
    }
