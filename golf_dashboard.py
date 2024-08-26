import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import matplotlib.pyplot as plt
from datetime import datetime
from initialize_db import initialize_db
from data_preprocessing import preprocess_data


st.set_page_config(
    page_title="Golf Dashboard",
    page_icon="⛳",
    layout="wide",
    initial_sidebar_state="expanded",
)

alt.themes.enable("dark")


def load_data_from_db(table="shots"):
    conn = sqlite3.connect("golf_data.db")
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)

    df["time"] = pd.to_datetime(df["time"])  # Konvertiert 'Time' in ein Datetime-Objekt

    conn.close()
    return df


def insert_data_into_db(df, club_type, table="shots"):
    conn = sqlite3.connect("golf_data.db")
    c = conn.cursor()

    # Füge den Schläger-Typ zu jedem Datensatz hinzu
    df = preprocess_data(df, club_type)

    # Daten in die Datenbank einfügen
    df.to_sql(table, conn, if_exists="append", index=False)

    conn.commit()
    conn.close()


# Funktion zur Erstellung eines angepassten Scatter-Plots mit Testdaten
def plot_custom_dispersion_chart(df):
    x_min, x_max = -40, 40
    fig = px.scatter(
        df,
        x="deflection_distance",
        y="total_yd",
        labels={
            "Deflection Distance": "Deflection Distance (yd)",
            "Total[yd]": "Total Distance (yd)",
        },
    )

    # Anpassungen vornehmen:
    fig.update_xaxes(
        # autorange="reversed",  # Vertauscht die Y-Achse
        autorange=False,  # Deaktiviere die automatische Bereichsanpassung
        range=[x_min, x_max],  # Setzt die Y-Achse symmetrisch
        # tickvals=[-20, -10, 0, 10, 20],  # Symmetrische Ticks
        scaleanchor="x",  # Stellt sicher, dass die Achsen proportional sind
        zeroline=True,  # Zeigt eine Linie bei y=0
        zerolinecolor="red",
    )

    # Setze den Plot auf eine feste Breite und Höhe und füge einen Rahmen hinzu
    fig.update_layout(
        width=450,
        height=500,
        xaxis_title="Deflection Distance (yd)",
        yaxis_title="Total Distance (yd)",
        # plot_bgcolor="rgba(144, 238, 144, 0.3)",  # Leichter Grünton für den Hintergrund
        paper_bgcolor="rgba(0,0,0,0)",  # Transparenter Hintergrund
        margin=dict(l=40, r=40, t=40, b=40),  # Rand um den Plot
        showlegend=False,  # Keine Legende anzeigen
    )

    return fig


def plot_avg_distance_over_time(df):
    # Extrahiere nur das Datum aus der Time-Spalte und formatiere es korrekt
    df["time"] = pd.to_datetime(df["time"])

    # Extrahiere nur das Datum aus der Time-Spalte
    df["date"] = df["time"].dt.floor("d")

    # Gruppiere nach Datum und berechne den Durchschnitt der Total Distance
    df_avg = df.groupby("date", as_index=False)["total_yd"].mean()

    # Runde den Durchschnittswert der Total Distance auf zwei Dezimalstellen
    df_avg["total_yd"] = df_avg["total_yd"].round(2)

    # Erstelle das Liniendiagramm
    fig = px.line(
        df_avg,
        x="date",
        y="total_yd",
        labels={"date": "Date", "total_yd": "Average Distance (yd)"},
        title="Average Total Distance Over Time",
    )

    fig.update_layout(
        width=400,
        height=300,
        xaxis_title="Date",
        yaxis_title="Average Distance (yd)",
        xaxis=dict(tickformat="%Y-%m-%d"),  # Formatierung der X-Achse
        paper_bgcolor="rgba(0,0,0,0)",  # Transparenter Hintergrund
        margin=dict(l=40, r=40, t=40, b=40),  # Rand um den Plot
        showlegend=False,  # Keine Legende anzeigen
    )

    return fig


# Histogramme in Spalten anordnen
def plot_histogram(data, parameter, num_bins, title):
    fig, ax = plt.subplots()
    ax.hist(data, bins=num_bins, edgecolor="black", alpha=0.7)

    avg_value = np.mean(data)
    ax.axvline(avg_value, color="red", linestyle="dashed", linewidth=1)
    min_ylim, max_ylim = ax.get_ylim()
    ax.text(avg_value, max_ylim * 0.9, f"Durchschnitt: {avg_value:.2f}", color="red")

    ax.set_title(title)
    ax.set_xlabel(parameter)
    ax.set_ylabel("Häufigkeit")

    st.pyplot(fig)


def main():
    # Datenbank initialisieren falls nicht vorhanden
    initialize_db()

    df = load_data_from_db()

    with st.sidebar:
        st.title("⛳ Golf Data Dashboard")

        club = st.selectbox("Wähle den Schläger aus:", df["type"].unique())
        date_range = st.date_input(
            "Wähle den Zeitraum aus:",
            [df["time"].min().date(), df["time"].max().date()],
        )

        start_date = datetime.combine(date_range[0], datetime.min.time())
        end_date = datetime.combine(date_range[1], datetime.max.time())

        filtered_df = df[
            (df["type"] == club) & (df["time"] >= start_date) & (df["time"] <= end_date)
        ]

        avg_total_distance = filtered_df["total_yd"].mean()
        avg_carry_distance = filtered_df["carry_yd"].mean()
        avg_club_speed = filtered_df["club_speed_mph"].mean()
        avg_launch_angle = filtered_df["launch_angle"].mean()

        max_total_distance = filtered_df["total_yd"].max()
        max_carry_distance = filtered_df["carry_yd"].max()
        max_club_speed = filtered_df["club_speed_mph"].max()

        st.markdown("### Durchschnittswerte")

        st.markdown(f"**Total Distance**: {avg_total_distance:.2f} yd")
        st.markdown(f"**Carry Distance**: {avg_carry_distance:.2f} yd")
        st.markdown(f"**Club Speed**: {avg_club_speed:.2f} mph")
        st.markdown(f"**Launch Angle**: {avg_launch_angle:.2f} °")

        st.markdown("### Bestmarken")

        st.markdown(f"**Top Distance**: {max_total_distance} yd")
        st.markdown(f"**Top Carry Distance**: {max_carry_distance} yd")
        st.markdown(f"**Top Club Speed**: {max_club_speed} mph")

        st.markdown("---")  # Fügt eine horizontale Linie ein

        # CSV-Datei hochladen
        uploaded_file = st.file_uploader("Lade eine CSV-Datei hoch", type=["csv"])

        # Schläger auswählen
        club = st.selectbox(
            "Wähle den Schläger aus:",
            [
                "3I",
                "4I",
                "5I",
                "6I",
                "7I",
                "8I",
                "9I",
                "PW",
                "SW",
                "LW",
                "DR",
                "2W",
                "3W",
            ],
        )

        # Import-Button
        if st.button("CSV importieren und in die Datenbank einfügen"):
            if uploaded_file is not None and club:
                # Lade die CSV-Datei in einen DataFrame
                df = pd.read_csv(uploaded_file)

                # Füge die Daten in die Datenbank ein
                insert_data_into_db(df, club)

                st.success(
                    f"Die Daten aus der Datei wurden erfolgreich mit dem Schläger '{club}' importiert."
                )

                # Laden der Daten aus der Datenbank und Anzeige im Dashboard
                df = load_data_from_db()
                st.dataframe(df)

    # Anzeige der beiden Charts nebeneinander in der obersten Zeile
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Shot Dispersion Chart")
        fig_dispersion = plot_custom_dispersion_chart(df)
        st.plotly_chart(fig_dispersion, use_container_width=True)

    with col2:
        st.subheader("Total Distance Over Time")
        fig_distance_over_time = plot_avg_distance_over_time(df)
        st.plotly_chart(fig_distance_over_time, use_container_width=True)

    # Histogramme in Spalten anordnen
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.subheader("Total Distance")
        plot_histogram(
            filtered_df["total_yd"],
            "Total Distance [yd]",
            num_bins=10,
            title="Total Distance",
        )

    with col2:
        st.subheader("Carry Distance")
        plot_histogram(
            filtered_df["carry_yd"],
            "Carry Distance [yd]",
            num_bins=10,
            title="Carry Distance",
        )

    with col3:
        st.subheader("Club Speed")
        plot_histogram(
            filtered_df["club_speed_mph"],
            "Club Speed [mph]",
            num_bins=10,
            title="Club Speed",
        )

    with col4:
        st.subheader("Launch Angle")
        plot_histogram(
            filtered_df["launch_angle"],
            "Launch Angle [°]",
            num_bins=20,
            title="Launch Angle",
        )


if __name__ == "__main__":
    main()
