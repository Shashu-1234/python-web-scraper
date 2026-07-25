"""Flask web interface for the Python Web Scraper."""

from __future__ import annotations

import csv
import io
from http import HTTPStatus

import requests
from flask import Flask, Response, jsonify, render_template, request

from scraper import Quote, scrape_quotes

app = Flask(__name__)

MAX_WEB_PAGES = 5


def requested_page_count() -> int:
    """Return a validated page count from a form, query string, or JSON body."""
    payload = request.get_json(silent=True) or {}
    raw_value = request.args.get("pages") or request.form.get("pages")
    raw_value = raw_value or payload.get("pages") or 1

    try:
        page_count = int(raw_value)
    except (TypeError, ValueError) as error:
        raise ValueError("Pages must be a whole number.") from error

    if not 1 <= page_count <= MAX_WEB_PAGES:
        raise ValueError(f"Pages must be between 1 and {MAX_WEB_PAGES}.")
    return page_count


def quote_payload(record: Quote) -> dict[str, object]:
    """Convert a quote record into a JSON-safe dictionary."""
    return {
        "quote": record.text,
        "author": record.author,
        "tags": list(record.tags),
    }


def collect_quotes() -> tuple[list[Quote] | None, tuple[Response, int] | None]:
    """Validate the request and run the scraper with web-safe limits."""
    try:
        pages = requested_page_count()
        records = scrape_quotes(
            max_pages=pages,
            delay_seconds=0.2,
            timeout_seconds=12.0,
        )
    except ValueError as error:
        response = jsonify({"ok": False, "error": str(error)})
        return None, (response, HTTPStatus.BAD_REQUEST)
    except requests.RequestException:
        response = jsonify(
            {
                "ok": False,
                "error": "The source website is temporarily unavailable. Try again shortly.",
            }
        )
        return None, (response, HTTPStatus.BAD_GATEWAY)

    return records, None


@app.get("/")
def home() -> str:
    """Render the web-scraper dashboard."""
    return render_template("index.html", max_pages=MAX_WEB_PAGES)


@app.post("/api/scrape")
def scrape_api() -> tuple[Response, int] | Response:
    """Scrape quotes and return structured JSON."""
    records, error = collect_quotes()
    if error is not None:
        return error

    assert records is not None
    return jsonify(
        {
            "ok": True,
            "count": len(records),
            "source": "https://quotes.toscrape.com/",
            "records": [quote_payload(record) for record in records],
        }
    )


@app.get("/api/download")
def download_csv() -> tuple[Response, int] | Response:
    """Scrape quotes and return a downloadable CSV file."""
    records, error = collect_quotes()
    if error is not None:
        return error

    assert records is not None
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=("quote", "author", "tags"))
    writer.writeheader()
    for record in records:
        writer.writerow(
            {
                "quote": record.text,
                "author": record.author,
                "tags": ", ".join(record.tags),
            }
        )

    csv_bytes = ("\ufeff" + output.getvalue()).encode("utf-8")
    return Response(
        csv_bytes,
        mimetype="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": 'attachment; filename="quotes.csv"',
            "Cache-Control": "no-store",
        },
    )


@app.get("/api/health")
def health() -> Response:
    """Return a lightweight deployment health response."""
    return jsonify({"ok": True, "service": "python-web-scraper"})


@app.errorhandler(404)
def not_found(_error: Exception) -> tuple[Response, int]:
    """Return JSON for unknown API paths and HTML navigation mistakes."""
    return (
        jsonify({"ok": False, "error": "The requested page was not found."}),
        HTTPStatus.NOT_FOUND,
    )


if __name__ == "__main__":
    app.run(debug=True)
