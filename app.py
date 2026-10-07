import sqlite3
from datetime import datetime
from flask import Flask, render_template, abort, request, redirect, url_for

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


def validasi_input(form):
    """Mengembalikan (daftar_error, data_bersih)."""
    errors = []

    # 1. Field wajib tidak boleh kosong
    labels = {
        "nim": "NIM",
        "nama": "Nama",
        "program_studi": "Program studi",
        "angkatan": "Angkatan",
        "ipk": "IPK",
    }
    for field, label in labels.items():
        if not form[field]:
            errors.append(f"{label} wajib diisi.")

    if errors:
        return errors, None

    # 2. Tipe data harus angka yang valid
    try:
        nim = int(form["nim"])
    except ValueError:
        errors.append("NIM harus berupa angka.")
    try:
        angkatan = int(form["angkatan"])
    except ValueError:
        errors.append("Angkatan harus berupa angka.")
    try:
        ipk = float(form["ipk"].replace(",", "."))
    except ValueError:
        errors.append("IPK harus berupa angka.")

    if errors:
        return errors, None

    # 3. IPK harus di rentang 0.00 - 4.00
    if ipk < 0.0 or ipk > 4.0:
        errors.append("IPK harus di antara 0.00 dan 4.00.")
        return errors, None

    data = {
        "nim": nim,
        "nama": form["nama"],
        "program_studi": form["program_studi"],
        "angkatan": angkatan,
        "ipk": ipk,
    }
    return errors, data


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


@app.route("/tambah", methods=["GET", "POST"])
def tambah():
    errors = []
    form = {"nim": "", "nama": "", "program_studi": "", "angkatan": "", "ipk": ""}

    if request.method == "POST":
        # Ambil input, buang spasi di awal/akhir
        form = {k: request.form.get(k, "").strip() for k in form}
        errors, data = validasi_input(form)

        if not errors:
            conn = get_db()
            # 4. Cek NIM duplikat
            ada = conn.execute(
                "SELECT 1 FROM mahasiswa WHERE nim = ?", (data["nim"],)
            ).fetchone()
            if ada:
                errors.append(f"NIM {data['nim']} sudah terdaftar.")
            else:
                # Query berparameter (?) supaya aman dari SQL injection
                conn.execute(
                    "INSERT INTO mahasiswa (nim, nama, program_studi, angkatan, ipk) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (data["nim"], data["nama"], data["program_studi"],
                     data["angkatan"], data["ipk"]),
                )
                conn.commit()
                conn.close()
                return redirect(url_for("index"))
            conn.close()

    # GET, atau POST yang gagal validasi: form tampil lagi dengan isian lama
    return render_template("form.html", form=form, errors=errors, mode="tambah")

@app.route("/ubah/<int:nim>", methods=["GET", "POST"])
def ubah(nim):
    conn = get_db()
    row = conn.execute("SELECT * FROM mahasiswa WHERE nim = ?", (nim,)).fetchone()

    if row is None:
        conn.close()
        abort(404)

    errors = []
    # GET: form diisi data lama dari database
    form = {
        "nim": str(row["nim"]),
        "nama": row["nama"],
        "program_studi": row["program_studi"],
        "angkatan": str(row["angkatan"]),
        "ipk": str(row["ipk"]),
    }

    if request.method == "POST":
        form = {k: request.form.get(k, "").strip() for k in form}
        # NIM dikunci: selalu pakai NIM dari URL, abaikan kiriman form
        form["nim"] = str(nim)
        errors, data = validasi_input(form)

        if not errors:
            conn.execute(
                "UPDATE mahasiswa SET nama = ?, program_studi = ?, "
                "angkatan = ?, ipk = ? WHERE nim = ?",
                (data["nama"], data["program_studi"],
                 data["angkatan"], data["ipk"], nim),
            )
            conn.commit()
            conn.close()
            return redirect(url_for("index"))

    conn.close()
    return render_template("form.html", form=form, errors=errors, mode="ubah")


@app.route("/hapus/<int:nim>", methods=["POST"])
def hapus(nim):
    conn = get_db()
    row = conn.execute("SELECT 1 FROM mahasiswa WHERE nim = ?", (nim,)).fetchone()

    if row is None:
        conn.close()
        abort(404)

    conn.execute("DELETE FROM mahasiswa WHERE nim = ?", (nim,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))
    
if __name__ == "__main__":
    init_db()
    app.run(debug=True)