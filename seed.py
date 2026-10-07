import sqlite3

conn = sqlite3.connect("mahasiswa.db")
conn.executemany(
    "INSERT OR IGNORE INTO mahasiswa VALUES (?, ?, ?, ?, ?)",
    [
        (21120122140001, "Budi Santoso", "Bisnis Digital", 2022, 3.45),
        (21120123140002, "Siti Aminah", "Bisnis Digital", 2023, 3.80),
        (21120121140003, "Andi Wijaya", "Bisnis Digital", 2021, 3.10),
    ],
)
conn.commit()
conn.close()
print("Data uji dimasukkan")