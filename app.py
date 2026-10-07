import sqlite3
from datetime import datetime
from flask import Flask, render_template, abort

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


def hitung_lama_studi(angkatan):
    # Dihitung otomatis, tidak disimpan di database
    return datetime.now().year - angkatan


@app.route("/")
def index():
    conn = get_db()
    rows = conn.execute("SELECT * FROM mahasiswa ORDER BY nim").fetchall()
    conn.close()

    data = []
    for r in rows:
        m = dict(r)
        m["lama_studi"] = hitung_lama_studi(m["angkatan"])
        data.append(m)

    return render_template("index.html", mahasiswa=data)


@app.route("/mahasiswa/<int:nim>")
def detail(nim):
    conn = get_db()
    row = conn.execute("SELECT * FROM mahasiswa WHERE nim = ?", (nim,)).fetchone()
    conn.close()

    if row is None:
        abort(404)

    m = dict(row)
    m["lama_studi"] = hitung_lama_studi(m["angkatan"])
    return render_template("detail.html", m=m)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)