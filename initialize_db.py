import sqlite3


def initialize_db():
    # Verbindung zur SQLite-Datenbank herstellen (oder Datenbank erstellen)
    conn = sqlite3.connect("golf_data.db")
    c = conn.cursor()

    # Tabelle für Golf-Daten erstellen
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS shots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time TEXT,
        total_yd REAL,
        carry_yd REAL,
        height_m REAL,
        smash_factor REAL,
        club_speed_mph REAL,
        ball_speed_mph REAL,
        launch_angle REAL,
        launch_direction REAL,
        deflection_distance REAL,
        type TEXT
    )
    """
    )

    # Änderungen speichern und Verbindung schließen
    conn.commit()
    conn.close()
