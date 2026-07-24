from unittest.mock import patch

from app import app
from scraper import Quote


def test_home_page_loads() -> None:
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"Python Web Scraper" in response.data
    assert b"Run scraper" in response.data


def test_health_endpoint() -> None:
    client = app.test_client()

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "ok": True,
        "service": "python-web-scraper",
    }


@patch("app.scrape_quotes")
def test_scrape_endpoint_returns_records(mock_scrape) -> None:
    mock_scrape.return_value = [
        Quote(text="A quote", author="An author", tags=("python", "testing"))
    ]
    client = app.test_client()

    response = client.post("/api/scrape", json={"pages": 1})

    assert response.status_code == 200
    assert response.get_json()["records"] == [
        {
            "quote": "A quote",
            "author": "An author",
            "tags": ["python", "testing"],
        }
    ]


def test_scrape_endpoint_rejects_invalid_page_count() -> None:
    client = app.test_client()

    response = client.post("/api/scrape", json={"pages": 99})

    assert response.status_code == 400
    assert response.get_json()["ok"] is False


@patch("app.scrape_quotes")
def test_csv_download(mock_scrape) -> None:
    mock_scrape.return_value = [
        Quote(text="A quote", author="An author", tags=("one", "two"))
    ]
    client = app.test_client()

    response = client.get("/api/download?pages=1")

    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert "quotes.csv" in response.headers["Content-Disposition"]
    assert b"A quote,An author" in response.data
