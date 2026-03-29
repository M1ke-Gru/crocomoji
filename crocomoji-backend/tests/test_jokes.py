"""Tests for the jokes service."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

import services.jokes as jokes_module
from services.jokes import fetch_jokes


class TestFetchJokes:
    async def test_returns_requested_count(self):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "jokes": [
                {"type": "twopart", "setup": f"Setup {i}", "delivery": "delivery"}
                for i in range(10)
            ]
        }

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_cls.return_value = mock_client

            result = await fetch_jokes(3)

        assert len(result) == 3

    async def test_extracts_setup_only(self):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "jokes": [
                {"type": "twopart", "setup": "Why so serious?", "delivery": "Because Joker"},
            ]
        }

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_cls.return_value = mock_client

            result = await fetch_jokes(1)

        assert result[0] == "Why so serious?"
        assert "Because Joker" not in result[0]

    async def test_falls_back_on_network_error(self):
        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = AsyncMock(side_effect=Exception("network error"))
            mock_client_cls.return_value = mock_client

            result = await fetch_jokes(3)

        assert len(result) == 3
        for setup in result:
            assert isinstance(setup, str)
            assert len(setup) > 0

    async def test_fills_gaps_when_api_returns_fewer(self):
        """If the API returns fewer jokes than requested, fallbacks fill the rest."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "jokes": [
                {"type": "twopart", "setup": "Only one joke", "delivery": "ha"},
            ]
        }

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_cls.return_value = mock_client

            # Reset fallback index
            jokes_module._fallback_index = 0
            result = await fetch_jokes(3)

        assert len(result) == 3

    async def test_skips_non_twopart_jokes(self):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "jokes": [
                {"type": "single", "joke": "I told a joke once."},
                {"type": "twopart", "setup": "Valid setup", "delivery": "delivery"},
            ]
        }

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_cls.return_value = mock_client

            jokes_module._fallback_index = 0
            result = await fetch_jokes(1)

        assert result[0] == "Valid setup"
