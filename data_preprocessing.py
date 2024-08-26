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
def preprocess_data(df, club):
    # df = pd.read_csv(file_path)
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

    df.rename(
        columns={
            "Time": "time",
            "Total[yd]": "total_yd",
            "Carry[yd]": "carry_yd",
            "Height[m]": "height_m",
            "Smash Factor": "smash_factor",
            "Club Speed[mph]": "club_speed_mph",
            "Ball Speed[mph]": "ball_speed_mph",
            "Launch Angle": "launch_angle",
            "Launch Direction": "launch_direction",
            "Type": "type",
            "Deflection Distance": "deflection_distance",
        },
        inplace=True,
    )

    return df
