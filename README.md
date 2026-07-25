# Python Web Scraper

[![Tests](https://github.com/Shashu-1234/python-web-scraper/actions/workflows/tests.yml/badge.svg)](https://github.com/Shashu-1234/python-web-scraper/actions/workflows/tests.yml)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An open-source Python project that extracts quotes, authors, and tags from
[Quotes to Scrape](https://quotes.toscrape.com/) and stores them in a CSV file.
The website is intended for web-scraping practice.

**Live application:** [python-web-scraper-tau.vercel.app](https://python-web-scraper-tau.vercel.app)

## Features

- Scrapes every available page or a user-defined number of pages.
- Extracts quote text, author names, and tags.
- Saves UTF-8 CSV output that opens correctly in Excel.
- Includes request timeouts, retries, logging, and polite request delays.
- Includes automated tests, linting, and GitHub Actions.
- Includes a responsive Flask interface with JSON and CSV endpoints.
- Requires code-owner review for pull requests when branch protection is enabled.

## Project Structure

```text
python-web-scraper/
├── .github/
│   ├── workflows/
│   │   └── tests.yml
│   ├── CODEOWNERS
│   └── pull_request_template.md
├── data/
│   └── .gitkeep
├── templates/
│   └── index.html
├── tests/
│   ├── test_app.py
│   └── test_scraper.py
├── .gitignore
├── app.py
├── CONTRIBUTING.md
├── LICENSE
├── pyproject.toml
├── README.md
├── requirements-dev.txt
├── requirements.txt
├── scraper.py
└── vercel.json
```

## Requirements

- Python 3.10 or newer
- Git

## Installation

Clone the repository:

```bash
git clone https://github.com/Shashu-1234/python-web-scraper.git
cd python-web-scraper
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

Install the runtime dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Usage

### Web application

Run the Flask interface locally:

```bash
flask --app app run --debug
```

Open `http://127.0.0.1:5000`, select how many pages to scrape, and choose
**Run scraper** or **Download CSV**.

Available endpoints:

```text
GET  /api/health
POST /api/scrape
GET  /api/download?pages=1
```

### Command-line application

Scrape all available pages:

```bash
python scraper.py
```

Scrape only the first three pages:

```bash
python scraper.py --max-pages 3
```

Choose a different CSV destination:

```bash
python scraper.py --output data/quotes.csv
```

Available options:

```text
--url URL           Starting page URL
--output PATH       Destination CSV path
--max-pages NUMBER  Maximum number of pages
--delay SECONDS     Delay between requests
--timeout SECONDS   HTTP request timeout
```

The default output is:

```text
data/output.csv
```

## Example CSV Output

```csv
quote,author,tags
"“The world as we have created it is a process of our thinking.”",Albert Einstein,"change, deep-thoughts, thinking, world"
"“It is our choices, Harry, that show what we truly are.”",J.K. Rowling,"abilities, choices"
```

## Running Tests

Install the development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run the linter and tests:

```bash
ruff check .
pytest
```

## Common Problems

### `ModuleNotFoundError`

Activate the virtual environment and run:

```bash
pip install -r requirements.txt
```

### Empty CSV

The target website's HTML may have changed. Review the selectors in
`parse_quotes()` and update the tests before changing them.

### `403 Forbidden`

The target website may not permit automated access. Check its terms of service
and `robots.txt`. Do not bypass access restrictions or anti-bot controls.

### Timeout

Check your internet connection, increase `--timeout`, and confirm that the
website is available.

## Responsible Use

- Scrape only public information you are permitted to access.
- Review the website's terms and `robots.txt`.
- Use reasonable delays and request rates.
- Do not collect private, confidential, or restricted data.
- Do not bypass authentication, CAPTCHAs, rate limits, or security controls.

## Contributing

Contributions must use a separate branch and a pull request:

```bash
git checkout -b feature/short-description
git add .
git commit -m "Add: short description"
git push origin feature/short-description
```

Open a pull request from the feature branch into `main`. Do not push directly
to `main`. The pull request must pass tests and receive the required code-owner
approval before merging.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the complete workflow.

## Branch Protection

The intended `main` branch rules are:

- Require a pull request before merging.
- Require at least one approval.
- Require review from code owners.
- Dismiss stale approvals when new commits are pushed.
- Require the `test` status check to pass.
- Block force pushes and branch deletion.
- Apply the rules to administrators.

The repository-wide code owner is defined in `.github/CODEOWNERS`:

```text
* @Shashu-1234
```

## License

This project is licensed under the [MIT License](LICENSE).

## Author

**Shashank Aushekar**

- GitHub: [@Shashu-1234](https://github.com/Shashu-1234)

## Support

Open a GitHub issue containing:

- A clear problem description.
- Steps to reproduce it.
- Expected and actual results.
- Your Python version and operating system.
