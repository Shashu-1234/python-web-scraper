from pathlib import Path

import pytest

from scraper import Quote, parse_quotes, scrape_quotes, write_csv


SAMPLE_HTML = """
<html>
  <body>
    <div class="quote">
      <span class="text">“A test quote.”</span>
      <small class="author">Test Author</small>
      <div class="tags">
        <a class="tag">testing</a>
        <a class="tag">python</a>
      </div>
    </div>
    <li class="next"><a href="/page/2/">Next</a></li>
  </body>
</html>
"""


def test_parse_quotes_extracts_record_and_next_page() -> None:
    records, next_path = parse_quotes(SAMPLE_HTML)

    assert records == [
        Quote(
            text="“A test quote.”",
            author="Test Author",
            tags=("testing", "python"),
        )
    ]
    assert next_path == "/page/2/"


def test_parse_quotes_handles_empty_page() -> None:
    records, next_path = parse_quotes("<html><body></body></html>")

    assert records == []
    assert next_path is None


def test_write_csv_creates_expected_file(tmp_path: Path) -> None:
    output_path = tmp_path / "data" / "output.csv"

    write_csv(
        [Quote(text="A quote", author="An author", tags=("one", "two"))],
        output_path,
    )

    content = output_path.read_text(encoding="utf-8-sig")
    assert "quote,author,tags" in content
    assert 'A quote,An author,"one, two"' in content


@pytest.mark.parametrize(
    ("max_pages", "delay", "timeout"),
    [
        (0, 0.5, 15.0),
        (1, -0.1, 15.0),
        (1, 0.5, 0.0),
    ],
)
def test_scrape_quotes_rejects_invalid_arguments(
    max_pages: int, delay: float, timeout: float
) -> None:
    with pytest.raises(ValueError):
        scrape_quotes(
            max_pages=max_pages,
            delay_seconds=delay,
            timeout_seconds=timeout,
        )
