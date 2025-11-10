Minimal Flask Pastebin

This is a tiny pastebin built with Flask. Features:

- Create a paste (title + content)
- View a paste by id
- List recent pastes

Quick start (macOS / zsh):

```bash
python3 -m venv .venv
source .venv/bin/activate
.venv/bin/pip install -r requirements.txt
# Run the app
FLASK_APP=app.py FLASK_ENV=development flask run
# Or: python app.py
```

Run tests:

```bash
.venv/bin/pytest -q
```
