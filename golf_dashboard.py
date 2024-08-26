import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(
    page_title="Golf Dashboard",
    page_icon="⛳",
    layout="wide",
    initial_sidebar_state="expanded",
)

alt.themes.enable("dark")


def load_data(file_path):
    df = pd.read_csv(file_path)
    df["Time"] = pd.to_datetime(df["Time"])
    return df


# Funktion zur Erstellung eines angepassten Scatter-Plots mit Testdaten
def plot_custom_dispersion_chart(df):
    x_min, x_max = -40, 40
    fig = px.scatter(
        df,
        x="Deflection Distance",
        y="Total[yd]",
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
    df["Time"] = pd.to_datetime(df["Time"])

    # Extrahiere nur das Datum aus der Time-Spalte
    df["Date"] = df["Time"].dt.floor("d")

    # Gruppiere nach Datum und berechne den Durchschnitt der Total Distance
    df_avg = df.groupby("Date", as_index=False)["Total[yd]"].mean()

    # Runde den Durchschnittswert der Total Distance auf zwei Dezimalstellen
    df_avg["Total[yd]"] = df_avg["Total[yd]"].round(2)

    # Erstelle das Liniendiagramm
    fig = px.line(
        df_avg,
        x="Date",
        y="Total[yd]",
        labels={"Date": "Date", "Total[yd]": "Average Distance (yd)"},
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
    df = load_data("processed_7I_Golfboy_SHOT_20240823.csv")

    with st.sidebar:
        st.title("⛳ Golf Data Dashboard")

        club = st.selectbox("Wähle den Schläger aus:", df["Type"].unique())
        date_range = st.date_input(
            "Wähle den Zeitraum aus:",
            [df["Time"].min().date(), df["Time"].max().date()],
        )

        start_date = datetime.combine(date_range[0], datetime.min.time())
        end_date = datetime.combine(date_range[1], datetime.max.time())

        filtered_df = df[
            (df["Type"] == club) & (df["Time"] >= start_date) & (df["Time"] <= end_date)
        ]

        avg_total_distance = filtered_df["Total[yd]"].mean()
        avg_carry_distance = filtered_df["Carry[yd]"].mean()
        avg_club_speed = filtered_df["Club Speed[mph]"].mean()
        avg_launch_angle = filtered_df["Launch Angle"].mean()

        max_total_distance = filtered_df["Total[yd]"].max()
        max_carry_distance = filtered_df["Carry[yd]"].max()
        max_club_speed = filtered_df["Club Speed[mph]"].max()

        st.markdown("### Durchschnittswerte")

        st.markdown(f"**Total Distance**: {avg_total_distance:.2f} yd")
        st.markdown(f"**Carry Distance**: {avg_carry_distance:.2f} yd")
        st.markdown(f"**Club Speed**: {avg_club_speed:.2f} mph")
        st.markdown(f"**Launch Angle**: {avg_launch_angle:.2f} °")

        st.markdown("### Bestmarken")

        st.markdown(f"**Top Distance**: {max_total_distance} yd")
        st.markdown(f"**Top Carry Distance**: {max_carry_distance} yd")
        st.markdown(f"**Top Club Speed**: {max_club_speed} mph")

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
            filtered_df["Total[yd]"],
            "Total Distance [yd]",
            num_bins=10,
            title="Total Distance",
        )

    with col2:
        st.subheader("Carry Distance")
        plot_histogram(
            filtered_df["Carry[yd]"],
            "Carry Distance [yd]",
            num_bins=10,
            title="Carry Distance",
        )

    with col3:
        st.subheader("Club Speed")
        plot_histogram(
            filtered_df["Club Speed[mph]"],
            "Club Speed [mph]",
            num_bins=10,
            title="Club Speed",
        )

    with col4:
        st.subheader("Launch Angle")
        plot_histogram(
            filtered_df["Launch Angle"],
            "Launch Angle [°]",
            num_bins=20,
            title="Launch Angle",
        )


if __name__ == "__main__":
    main()
