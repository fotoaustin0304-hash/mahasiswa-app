import sqlite3
from flask import Flask

app = Flask(__name__)
DB_NAME = "mahasiswa.db"


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS mahasiswa (
            nim INTEGER PRIMARY KEY,
            nama TEXT NOT NULL,
            program_studi TEXT NOT NULL,
            angkatan INTEGER NOT NULL,
            ipk REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def index():
    return "Aplikasi Data Mahasiswa berjalan!"


if __name__ == "__main__":
    init_db()
    app.run(debug=True)