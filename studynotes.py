import sqlite3
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs

DATABASE = Path(__file__).with_name("studynotes.sqlite3")


def create_database():
    with sqlite3.connect(DATABASE) as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS notes "
            "(id INTEGER PRIMARY KEY, content TEXT NOT NULL)"
        )


def create_page():
    with sqlite3.connect(DATABASE) as connection:
        notes = connection.execute(
            "SELECT content FROM notes ORDER BY id DESC"
        ).fetchall()

    note_list = "".join(f"<li>{escape(note[0])}</li>" for note in notes)
    if not note_list:
        note_list = "<li>Nu ai notițe încă.</li>"

    page = """<!doctype html>
<html lang="ro">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>StudyNotes</title>
    <style>
        body {
            margin: 0;
            background: #f3f6f2;
            color: #20342d;
            font-family: Arial, sans-serif;
        }

        main {
            max-width: 700px;
            margin: 80px auto;
            padding: 0 24px;
        }

        h1 {
            color: #28634f;
        }

        p {
            line-height: 1.6;
        }

        form {
            display: grid;
            gap: 12px;
            margin: 32px 0;
        }

        textarea {
            padding: 12px;
            font: inherit;
        }

        button {
            width: fit-content;
            padding: 10px 16px;
            border: 0;
            background: #28634f;
            color: white;
            cursor: pointer;
        }

        li {
            margin: 12px 0;
            line-height: 1.5;
        }
    </style>
</head>
<body>
    <main>
        <h1>StudyNotes</h1>
        <form method="post">
            <label for="content">Scrie o notiță</label>
            <textarea id="content" name="content" rows="4" required></textarea>
            <button type="submit">Salvează notița</button>
        </form>
        <h2>Notițele tale</h2>
        <ul>{note_list}</ul>
    </main>
</body>
</html>"""
    return page.replace("{note_list}", note_list)


class StudyNotesHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        page = create_page().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(page)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        form = parse_qs(self.rfile.read(length).decode("utf-8"))
        content = form.get("content", [""])[0].strip()

        if content:
            with sqlite3.connect(DATABASE) as connection:
                connection.execute(
                    "INSERT INTO notes (content) VALUES (?)", (content,)
                )

        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()

create_database()
server = HTTPServer(("127.0.0.1", 8000), StudyNotesHandler)
print("StudyNotes rulează la http://127.0.0.1:8000")

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("Serverul a fost oprit.")
    server.server_close()
