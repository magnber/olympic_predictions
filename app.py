"""
Olympic Predictions - Streamlit App

Visualiserer datagrunnlag og prediksjoner for Vinter-OL 2026.
"""

import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path

# Paths
DB_PATH = Path(__file__).parent / "db" / "olympics.db"
OUTPUT_DIR = Path(__file__).parent / "output"

st.set_page_config(
    page_title="Olympic Predictions 2026",
    page_icon="🏅",
    layout="wide"
)


def get_connection():
    return sqlite3.connect(DB_PATH)


@st.cache_data
def load_database_stats():
    """Load database statistics."""
    conn = get_connection()
    
    stats = {}
    
    # Table counts
    for table in ["countries", "sports", "competitions", "athletes", "entries", "excluded_athletes"]:
        df = pd.read_sql_query(f"SELECT COUNT(*) as count FROM {table}", conn)
        stats[table] = df["count"].iloc[0]
    
    # Entries by source
    df_sources = pd.read_sql_query(
        "SELECT source, COUNT(*) as count FROM entries GROUP BY source ORDER BY count DESC",
        conn
    )
    stats["entries_by_source"] = df_sources
    
    # Entries by sport
    df_sports = pd.read_sql_query("""
        SELECT 
            s.name as sport,
            COUNT(e.id) as entries
        FROM entries e
        JOIN competitions c ON e.competition_id = c.id
        JOIN sports s ON c.sport_id = s.id
        GROUP BY s.name
        ORDER BY entries DESC
    """, conn)
    stats["entries_by_sport"] = df_sports
    
    # Countries with most entries
    df_countries = pd.read_sql_query("""
        SELECT 
            a.country_code as country,
            COUNT(e.id) as entries
        FROM entries e
        JOIN athletes a ON e.athlete_id = a.id
        GROUP BY a.country_code
        ORDER BY entries DESC
        LIMIT 15
    """, conn)
    stats["top_countries"] = df_countries
    
    conn.close()
    return stats


@st.cache_data
def load_predictions():
    """Load prediction results."""
    pred_file = OUTPUT_DIR / "predictions.csv"
    if pred_file.exists():
        return pd.read_csv(pred_file)
    return None


@st.cache_data
def load_competition_predictions():
    """Load competition-level predictions."""
    comp_file = OUTPUT_DIR / "competition_predictions.csv"
    if comp_file.exists():
        return pd.read_csv(comp_file)
    return None


@st.cache_data
def load_athletes():
    """Load athletes from database."""
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT a.name, a.country_code as country, COUNT(e.id) as events
        FROM athletes a
        LEFT JOIN entries e ON a.id = e.athlete_id
        LEFT JOIN excluded_athletes ex ON a.id = ex.athlete_id
        WHERE ex.athlete_id IS NULL
        GROUP BY a.id
        ORDER BY events DESC
    """, conn)
    conn.close()
    return df


@st.cache_data
def load_entries_detail():
    """Load detailed entries."""
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT 
            a.name as athlete,
            a.country_code as country,
            c.name as competition,
            e.score,
            e.source
        FROM entries e
        JOIN athletes a ON e.athlete_id = a.id
        JOIN competitions c ON e.competition_id = c.id
        ORDER BY e.score DESC
    """, conn)
    conn.close()
    return df


# ============================================================
# MAIN APP
# ============================================================

st.title("🏅 Olympic Predictions 2026")
st.markdown("**Vinter-OL - Milano Cortina**")

# Sidebar navigation
page = st.sidebar.radio(
    "Navigasjon",
    ["Datagrunnlag", "Prediksjoner", "Konkurransedetaljer"]
)

# ============================================================
# PAGE: DATAGRUNNLAG
# ============================================================
if page == "Datagrunnlag":
    st.header("📊 Datagrunnlag")
    
    if not DB_PATH.exists():
        st.error(f"Database ikke funnet: {DB_PATH}")
        st.info("Kjør `python run_pipeline.py` for å opprette databasen.")
        st.stop()
    
    stats = load_database_stats()
    
    # Meta statistics
    st.subheader("Database Oversikt")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Utøvere", stats["athletes"])
    col2.metric("Konkurranser", stats["competitions"])
    col3.metric("Entries", stats["entries"])
    col4.metric("Ekskluderte", stats["excluded_athletes"])
    
    st.divider()
    
    # Entries by source
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Entries etter kilde")
        df_sources = stats["entries_by_source"]
        
        # Add percentage
        total = df_sources["count"].sum()
        df_sources["prosent"] = (df_sources["count"] / total * 100).round(1)
        df_sources["prosent"] = df_sources["prosent"].astype(str) + "%"
        
        st.dataframe(df_sources, use_container_width=True, hide_index=True)
        
        # Visual
        st.bar_chart(df_sources.set_index("source")["count"])
    
    with col2:
        st.subheader("Entries etter sport")
        df_sports = stats["entries_by_sport"]
        st.dataframe(df_sports, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Top countries
    st.subheader("Land med flest entries")
    df_countries = stats["top_countries"]
    st.bar_chart(df_countries.set_index("country")["entries"])
    
    st.divider()
    
    # Detailed data explorer
    st.subheader("Datautforsker")
    
    tab1, tab2 = st.tabs(["Utøvere", "Alle Entries"])
    
    with tab1:
        df_athletes = load_athletes()
        
        # Filter
        country_filter = st.multiselect(
            "Filtrer etter land",
            options=sorted(df_athletes["country"].unique()),
            default=["NOR", "SWE", "FIN"]
        )
        
        if country_filter:
            df_filtered = df_athletes[df_athletes["country"].isin(country_filter)]
        else:
            df_filtered = df_athletes
        
        st.dataframe(df_filtered, use_container_width=True, hide_index=True)
    
    with tab2:
        df_entries = load_entries_detail()
        
        # Filter by source
        source_filter = st.multiselect(
            "Filtrer etter kilde",
            options=df_entries["source"].unique(),
            default=list(df_entries["source"].unique())
        )
        
        if source_filter:
            df_entries_filtered = df_entries[df_entries["source"].isin(source_filter)]
        else:
            df_entries_filtered = df_entries
        
        st.dataframe(df_entries_filtered.head(100), use_container_width=True, hide_index=True)
        st.caption(f"Viser topp 100 av {len(df_entries_filtered)} entries")


# ============================================================
# PAGE: PREDIKSJONER
# ============================================================
elif page == "Prediksjoner":
    st.header("🏆 Medalje-prediksjoner")
    
    df_pred = load_predictions()
    
    if df_pred is None:
        st.error("Ingen prediksjoner funnet.")
        st.info("Kjør `python predict.py` for å generere prediksjoner.")
        st.stop()
    
    # Summary metrics
    st.subheader("Topp 10 Land")
    
    df_top10 = df_pred.head(10).copy()
    
    # Display as table with medal emojis
    df_display = df_top10.copy()
    df_display.columns = ["Land", "🥇 Gull", "🥈 Sølv", "🥉 Bronse", "Total"]
    df_display.index = range(1, len(df_display) + 1)
    df_display.index.name = "Rank"
    
    st.dataframe(df_display, use_container_width=True)
    
    st.divider()
    
    # Nordic countries detail
    st.subheader("Nordiske land")
    
    nordic = ["NOR", "SWE", "FIN", "DEN"]
    df_nordic = df_pred[df_pred["country"].isin(nordic)].copy()
    
    if not df_nordic.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        for i, (_, row) in enumerate(df_nordic.iterrows()):
            col = [col1, col2, col3, col4][i]
            with col:
                st.metric(
                    row["country"],
                    f"{row['total']} medaljer",
                    f"🥇{row['gold']} 🥈{row['silver']} 🥉{row['bronze']}"
                )
    
    st.divider()
    
    # Chart
    st.subheader("Medaljefordeling - Topp 15")
    
    df_chart = df_pred.head(15).set_index("country")[["gold", "silver", "bronze"]]
    st.bar_chart(df_chart)
    
    st.divider()
    
    # Full table
    st.subheader("Alle land")
    st.dataframe(df_pred, use_container_width=True, hide_index=True)


# ============================================================
# PAGE: KONKURRANSEDETALJER
# ============================================================
elif page == "Konkurransedetaljer":
    st.header("🎿 Konkurransedetaljer")
    
    df_comp = load_competition_predictions()
    
    if df_comp is None:
        st.error("Ingen konkurranseprediksjoner funnet.")
        st.stop()
    
    # Get unique competitions
    competitions = sorted(df_comp["competition"].unique())
    
    # Competition selector
    selected_comp = st.selectbox(
        "Velg konkurranse",
        competitions
    )
    
    if selected_comp:
        df_filtered = df_comp[df_comp["competition"] == selected_comp].copy()
        
        # Sort by medal probability
        df_filtered = df_filtered.sort_values("medal_prob", ascending=False)
        
        # Format probabilities as percentages
        for col in ["gold_prob", "silver_prob", "bronze_prob", "medal_prob"]:
            df_filtered[col] = (df_filtered[col] * 100).round(1)
        
        df_filtered = df_filtered.rename(columns={
            "athlete_name": "Utøver",
            "country": "Land",
            "gold_prob": "Gull %",
            "silver_prob": "Sølv %",
            "bronze_prob": "Bronse %",
            "medal_prob": "Medalje %"
        })
        
        # Show top medal contenders
        st.subheader(f"Medaljesannsynlighet: {selected_comp}")
        
        df_show = df_filtered[["Utøver", "Land", "Gull %", "Sølv %", "Bronse %", "Medalje %"]].head(20)
        st.dataframe(df_show, use_container_width=True, hide_index=True)
        
        # Country filter
        st.divider()
        st.subheader("Filtrer etter land")
        
        countries = sorted(df_filtered["Land"].unique())
        selected_countries = st.multiselect(
            "Velg land",
            countries,
            default=["NOR", "SWE"] if "NOR" in countries else []
        )
        
        if selected_countries:
            df_country = df_filtered[df_filtered["Land"].isin(selected_countries)]
            st.dataframe(
                df_country[["Utøver", "Land", "Gull %", "Sølv %", "Bronse %", "Medalje %"]],
                use_container_width=True,
                hide_index=True
            )


# ============================================================
# FOOTER
# ============================================================
st.sidebar.divider()
st.sidebar.markdown("""
**Data Pipeline**
- ISU API (skøyter)
- FIS Scraping (alpint)
- Legacy JSON (resten)

*Plackett-Luce Monte Carlo*
""")
