# Contributing

Thank you for contributing to Python Web Scraper.

## Required workflow

1. Accept the GitHub collaborator invitation or fork the repository.
2. Do not push directly to `main`.
3. Create a branch:

   ```bash
   git checkout -b feature/short-description
   ```

4. Install development dependencies:

   ```bash
   pip install -r requirements-dev.txt
   ```

5. Make focused changes and update the documentation or tests when needed.
6. Run:

   ```bash
   ruff check .
   pytest
   ```

7. Commit and push:

   ```bash
   git add .
   git commit -m "Add: short description"
   git push origin feature/short-description
   ```

8. Create a pull request targeting `main`.
9. Wait for the code owner's approval and successful status checks.

The repository owner is the required code owner for all files.
