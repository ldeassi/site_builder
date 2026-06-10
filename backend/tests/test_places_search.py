"""Tests for places_search module."""

from unittest.mock import AsyncMock, patch

import pytest

from modules.places_search import _format_category, _place_from_new_api, search_businesses_page


def test_format_category():
    assert _format_category("hair_salon", None) == "Hair Salon"
    assert _format_category(None, ["restaurant", "food"]) == "Restaurant"


def test_place_from_new_api():
    place = _place_from_new_api(
        {
            "id": "places/ChIJ123",
            "displayName": {"text": "Joe Pizza"},
            "formattedAddress": "123 Main St",
            "websiteUri": "https://joes.com",
            "nationalPhoneNumber": "+1 555-0100",
            "rating": 4.5,
            "userRatingCount": 10,
            "primaryType": "restaurant",
        }
    )
    assert place is not None
    assert place["placeId"] == "ChIJ123"
    assert place["name"] == "Joe Pizza"
    assert place["hasWebsite"] is True
    assert place["phone"] == "+1 555-0100"


@pytest.mark.asyncio
async def test_search_falls_back_to_legacy_on_new_api_failure():
    new_response = AsyncMock()
    new_response.status_code = 403
    new_response.content = b'{"error":{"message":"Places API (New) has not been enabled"}}'
    new_response.json = lambda: {"error": {"message": "Places API (New) has not been enabled"}}

    legacy_search_response = AsyncMock()
    legacy_search_response.content = b"{}"
    legacy_search_response.json = lambda: {
        "status": "OK",
        "results": [
            {
                "place_id": "ChIJabc",
                "name": "Local Shop",
                "formatted_address": "1 Oak Ave",
                "types": ["store"],
                "rating": 4.0,
                "user_rating_total": 5,
            }
        ],
        "next_page_token": "token-abc",
    }

    legacy_details_response = AsyncMock()
    legacy_details_response.content = b"{}"
    legacy_details_response.json = lambda: {
        "status": "OK",
        "result": {"website": "https://shop.example", "formatted_phone_number": "555-1234"},
    }

    mock_client = AsyncMock()

    async def mock_post(*args, **kwargs):
        return new_response

    async def mock_get(url, **kwargs):
        if "textsearch" in url:
            return legacy_search_response
        return legacy_details_response

    mock_client.post = mock_post
    mock_client.get = mock_get
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("modules.places_search.httpx.AsyncClient", return_value=mock_client):
        result = await search_businesses_page(
            api_key="test-key",
            query="businesses in Leesburg, VA",
            lat=39.1,
            lng=-77.5,
        )

    assert result["provider"] == "legacy"
    assert len(result["businesses"]) == 1
    assert result["businesses"][0]["name"] == "Local Shop"
    assert result["hasNextPage"] is True
    assert result["nextPageToken"] == "token-abc"
