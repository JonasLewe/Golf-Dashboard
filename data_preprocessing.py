import numpy as np
import pandas as pd
import argparse


def convert_launch_direction(value):
    if value.startswith("L"):
        return -float(value[1:])  # Entfernt 'L' und macht den Wert negativ
    elif value.startswith("R"):
        return float(value[1:])  # Entfernt 'R' und belässt den Wert positiv
    else:
        return None  # Falls ein anderer Wert auftaucht, wird None zurückgegeben


def create_deflection_distance_column(df):
    df["Launch Direction (rad)"] = np.deg2rad(df["Launch Direction"])

    # Berechne die Deflection Distance
    df["Deflection Distance"] = df["Total[yd]"] * np.sin(df["Launch Direction (rad)"])

    # Optional: Runde die Werte auf eine sinnvolle Genauigkeit
    df["Deflection Distance"] = df["Deflection Distance"].round(2)

    # Entferne die Launch Direction (rad) Spalte
    df = df.drop(columns=["Launch Direction (rad)"])

    return df


# Funktion, um das CSV zu verarbeiten
def process_file(file_path, club):
    df = pd.read_csv(file_path)
    df["Launch Direction"] = df["Launch Direction"].apply(convert_launch_direction)
    df["Type"] = club  # Setzt den Schläger-Typ in der 'Type'-Spalte

    df["Time"] = pd.to_datetime(df["Time"])  # Konvertiert 'Time' in ein Datetime-Objekt

    df = create_deflection_distance_column(df)

    float_columns = [
        "Total[yd]",
        "Carry[yd]",
        "Height[m]",
        "Smash Factor",
        "Club Speed[mph]",
        "Ball Speed[mph]",
        "Launch Angle",
        "Launch Direction",
        "Deflection Distance",
    ]

    for col in float_columns:
        # Konvertiere alle Werte erst zu Strings, dann ersetze das Komma und konvertiere zu float
        df[col] = df[col].astype(str).str.replace(",", ".").astype(float)

    # Optional: Speichern des verarbeiteten DataFrames in eine neue Datei
    output_file = f"processed_{club}_{file_path}"
    df.to_csv(output_file, index=False)
    print(f"Processed file saved as {output_file}")
    return df


# Main-Funktion mit Argument Parsing
def main():
    parser = argparse.ArgumentParser(
        description="Process a CSV file with launch direction data."
    )
    parser.add_argument("file", type=str, help="Path to the CSV file")
    parser.add_argument(
        "club",
        type=str,
        choices=[
            "3I",
            "4I",
            "5I",
            "6I",
            "7I",
            "8I",
            "9I",
            "DR",
            "2W",
            "3W",
            "5W",
            "PW",
            "SW",
            "LW",
        ],
        help="Golf club used in the session (e.g., 3I, 9I, DR, SW, 1W)",
    )

    # args = parser.parse_args()

    # Verarbeite das File
    # process_file(args.file, args.club)
    process_file("Golfboy_SHOT_20240823.csv", "7I")


if __name__ == "__main__":
    main()
