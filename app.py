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
    
    # Data quality by sport - shows source and score variance
    df_quality = pd.read_sql_query("""
        SELECT 
            s.name as sport,
            e.source,
            COUNT(DISTINCT c.id) as competitions,
            COUNT(e.id) as entries,
            ROUND(MIN(e.score), 0) as min_score,
            ROUND(MAX(e.score), 0) as max_score,
            ROUND(MAX(e.score) / MAX(MIN(e.score), 1), 2) as score_ratio
        FROM entries e
        JOIN competitions c ON e.competition_id = c.id
        JOIN sports s ON c.sport_id = s.id
        GROUP BY s.name, e.source
        ORDER BY s.name
    """, conn)
    stats["data_quality"] = df_quality
    
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


@st.cache_data
def load_historical_data():
    """Load historical Olympics data."""
    conn = get_connection()
    
    # Check if tables exist
    try:
        df_check = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='historical_medals'",
            conn
        )
        if df_check.empty:
            conn.close()
            return None
    except Exception:
        conn.close()
        return None
    
    data = {}
    
    # Olympics list
    data["olympics"] = pd.read_sql_query("""
        SELECT id, year, city, host_country, total_events
        FROM historical_olympics
        ORDER BY year DESC
    """, conn)
    
    # All medal data
    data["medals"] = pd.read_sql_query("""
        SELECT 
            ho.year, ho.city,
            hm.country_code, hm.country_name, hm.rank,
            hm.gold, hm.silver, hm.bronze, hm.total
        FROM historical_medals hm
        JOIN historical_olympics ho ON hm.olympics_id = ho.id
        ORDER BY ho.year DESC, hm.rank ASC
    """, conn)
    
    # Aggregated by country
    data["totals"] = pd.read_sql_query("""
        SELECT 
            country_code,
            country_name,
            SUM(gold) as gold,
            SUM(silver) as silver,
            SUM(bronze) as bronze,
            SUM(total) as total,
            COUNT(*) as appearances,
            ROUND(AVG(rank), 1) as avg_rank
        FROM historical_medals
        GROUP BY country_code
        ORDER BY gold DESC, silver DESC, bronze DESC
    """, conn)
    
    conn.close()
    return data


# ============================================================
# MAIN APP
# ============================================================

st.title("🏅 Olympic Predictions 2026")
st.markdown("**Vinter-OL - Milano Cortina**")

# Sidebar navigation
page = st.sidebar.radio(
    "Navigasjon",
    ["Datagrunnlag", "Historikk", "Predikasjon oversikt", "Drilldown"]
)

# ============================================================
# PAGE: DATAGRUNNLAG
# ============================================================
if page == "Datagrunnlag":
    st.header("📊 Datagrunnlag", anchor="datagrunnlag")
    
    if not DB_PATH.exists():
        st.error(f"Database ikke funnet: {DB_PATH}")
        st.info("Kjør `python run_pipeline.py` for å opprette databasen.")
        st.stop()
    
    stats = load_database_stats()
    
    # Meta statistics
    st.subheader("Database Oversikt", anchor="database-oversikt")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Utøvere", stats["athletes"])
    col2.metric("Konkurranser", stats["competitions"])
    col3.metric("Entries", stats["entries"])
    col4.metric("Ekskluderte", stats["excluded_athletes"])
    
    st.divider()
    
    # Entries by source
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Entries etter kilde", anchor="entries-kilde")
        df_sources = stats["entries_by_source"].copy()
        
        # Add percentage and description
        total = df_sources["count"].sum()
        df_sources["prosent"] = (df_sources["count"] / total * 100).round(1)
        df_sources["prosent"] = df_sources["prosent"].astype(str) + "%"
        
        # Add source descriptions
        source_desc = {
            "isu": "ISU API - Skøyter",
            "fis_alpine": "FIS Scraping - Alpint",
            "fis_xc": "FIS Scraping - Langrenn",
            "manual": "Legacy JSON"
        }
        df_sources["beskrivelse"] = df_sources["source"].map(source_desc).fillna(df_sources["source"])
        df_sources = df_sources[["beskrivelse", "count", "prosent"]]
        df_sources.columns = ["Kilde", "Entries", "Prosent"]
        
        st.dataframe(df_sources, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("Entries etter sport", anchor="entries-sport")
        df_sports = stats["entries_by_sport"]
        st.dataframe(df_sports, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Data quality section
    st.subheader("📋 Datakvalitet per sport", anchor="datakvalitet")
    st.caption("Score ratio = maks/min score. Høyere ratio = bedre differensiering mellom utøvere.")
    
    df_quality = stats["data_quality"].copy()
    
    # Add quality indicator
    def quality_indicator(row):
        if row["source"] in ["isu", "fis_alpine", "fis_xc"]:
            return "✓ Disiplin-spesifikk"
        elif row["score_ratio"] > 5:
            return "⚠ OK differensiering"
        else:
            return "✗ Lav differensiering"
    
    df_quality["kvalitet"] = df_quality.apply(quality_indicator, axis=1)
    
    # Rename columns
    df_quality = df_quality.rename(columns={
        "sport": "Sport",
        "source": "Kilde",
        "competitions": "Konkurranser",
        "entries": "Entries",
        "min_score": "Min Score",
        "max_score": "Max Score",
        "score_ratio": "Ratio",
        "kvalitet": "Kvalitet"
    })
    
    st.dataframe(df_quality, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Top countries
    st.subheader("Land med flest entries", anchor="topp-land")
    df_countries = stats["top_countries"]
    st.bar_chart(df_countries.set_index("country")["entries"])
    
    st.divider()
    
    # Detailed data explorer
    st.subheader("Datautforsker", anchor="datautforsker")
    
    tab1, tab2, tab3 = st.tabs(["Utøvere", "Alle Entries", "Langrenn Spesialisering"])
    
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
    
    with tab3:
        st.markdown("**Sprint vs Distance spesialisering**")
        st.caption("Viser hvordan FIS cross-country pipeline differensierer mellom sprint og distanse-løpere.")
        
        conn = get_connection()
        
        # Get cross-country entries with pivot
        df_xc = pd.read_sql_query("""
            SELECT 
                a.name as athlete,
                a.country_code as country,
                c.id as comp_id,
                e.score
            FROM entries e
            JOIN athletes a ON e.athlete_id = a.id
            JOIN competitions c ON e.competition_id = c.id
            WHERE e.source = 'fis_xc'
            ORDER BY e.score DESC
        """, conn)
        conn.close()
        
        if df_xc.empty:
            st.info("Ingen FIS langrenn-data funnet. Kjør `python run_pipeline.py xc`.")
        else:
            # Determine if sprint or distance
            df_xc["type"] = df_xc["comp_id"].apply(
                lambda x: "Sprint" if "sprint" in x else "Distance"
            )
            
            # Pivot to show sprint vs distance scores
            df_pivot = df_xc.pivot_table(
                index=["athlete", "country"],
                columns="type",
                values="score",
                aggfunc="first"
            ).reset_index()
            
            # Fill NaN with "-" for display
            df_pivot["Sprint"] = df_pivot["Sprint"].fillna(0)
            df_pivot["Distance"] = df_pivot["Distance"].fillna(0)
            
            # Add specialization indicator
            def specialization(row):
                if row["Sprint"] > 0 and row["Distance"] == 0:
                    return "🏃 Sprint-spesialist"
                elif row["Sprint"] == 0 and row["Distance"] > 0:
                    return "🎿 Distanse-spesialist"
                elif row["Sprint"] > 0 and row["Distance"] > 0:
                    ratio = row["Sprint"] / row["Distance"]
                    if ratio > 1.1:
                        return "↗️ Sprint-fokus"
                    elif ratio < 0.9:
                        return "↘️ Distanse-fokus"
                    else:
                        return "⚖️ Allrounder"
                return "-"
            
            df_pivot["Spesialisering"] = df_pivot.apply(specialization, axis=1)
            
            # Sort by total score
            df_pivot["total"] = df_pivot["Sprint"] + df_pivot["Distance"]
            df_pivot = df_pivot.sort_values("total", ascending=False)
            
            # Format for display
            df_pivot["Sprint"] = df_pivot["Sprint"].apply(lambda x: f"{int(x)}" if x > 0 else "-")
            df_pivot["Distance"] = df_pivot["Distance"].apply(lambda x: f"{int(x)}" if x > 0 else "-")
            
            df_display = df_pivot[["athlete", "country", "Sprint", "Distance", "Spesialisering"]].copy()
            df_display.columns = ["Utøver", "Land", "Sprint pts", "Distance pts", "Spesialisering"]
            
            # Filter
            country_filter_xc = st.multiselect(
                "Filtrer etter land",
                options=sorted(df_display["Land"].unique()),
                default=["NOR", "SWE", "FIN"],
                key="xc_country_filter"
            )
            
            if country_filter_xc:
                df_display = df_display[df_display["Land"].isin(country_filter_xc)]
            
            st.dataframe(df_display.head(50), use_container_width=True, hide_index=True)
            
            # Show stats
            col1, col2, col3 = st.columns(3)
            sprint_only = len(df_pivot[df_pivot["Sprint"] != "-"][df_pivot["Distance"] == "-"])
            dist_only = len(df_pivot[df_pivot["Distance"] != "-"][df_pivot["Sprint"] == "-"])
            both = len(df_pivot[(df_pivot["Sprint"] != "-") & (df_pivot["Distance"] != "-")])
            
            col1.metric("Sprint-spesialister", sprint_only)
            col2.metric("Distanse-spesialister", dist_only)
            col3.metric("Allroundere", both)


# ============================================================
# PAGE: HISTORIKK
# ============================================================
elif page == "Historikk":
    st.header("📜 Historiske resultater", anchor="historikk")
    st.markdown("**Medaljetabell fra de siste 4 vinter-OL (2010-2022)**")
    
    hist_data = load_historical_data()
    
    if hist_data is None:
        st.error("Ingen historiske data funnet.")
        st.info("Kjør `python run_pipeline.py hist` for å importere historiske data.")
        st.stop()
    
    # Summary - Total medals last 4 Olympics
    st.subheader("🏆 Samlet medaljetabell (2010-2022)", anchor="samlet-medaljetabell")
    
    df_totals = hist_data["totals"].copy()
    df_totals = df_totals.head(15)
    
    # Format for display
    df_display = df_totals[["country_code", "gold", "silver", "bronze", "total", "appearances", "avg_rank"]].copy()
    df_display.columns = ["Land", "🥇 Gull", "🥈 Sølv", "🥉 Bronse", "Total", "Deltakelser", "Snitt rank"]
    df_display.index = range(1, len(df_display) + 1)
    
    st.dataframe(df_display, use_container_width=True)
    
    st.divider()
    
    # Pivot table - Countries x Olympics
    st.subheader("📊 Medaljer per OL", anchor="medaljer-per-ol")
    st.caption("Land nedover, OL bortover - viser totalt antall medaljer")
    
    df_medals = hist_data["medals"].copy()
    
    # Create pivot table
    df_pivot = df_medals.pivot_table(
        index="country_code",
        columns="year",
        values="total",
        aggfunc="first"
    ).fillna(0).astype(int)
    
    # Sort by total medals
    df_pivot["Total"] = df_pivot.sum(axis=1)
    df_pivot = df_pivot.sort_values("Total", ascending=False)
    
    # Rename columns with city names
    olympics_info = {2022: "Beijing 2022", 2018: "PyeongChang 2018", 2014: "Sochi 2014", 2010: "Vancouver 2010"}
    df_pivot = df_pivot.rename(columns=olympics_info)
    
    # Show top 15
    df_pivot_display = df_pivot.head(15).copy()
    df_pivot_display.index.name = "Land"
    
    st.dataframe(df_pivot_display, use_container_width=True)
    
    st.divider()
    
    # Nordic countries focus
    st.subheader("🇳🇴 Nordiske land", anchor="nordiske-land")
    
    nordic_codes = ["NOR", "SWE", "FIN", "DEN"]
    df_nordic = hist_data["totals"][hist_data["totals"]["country_code"].isin(nordic_codes)].copy()
    
    if not df_nordic.empty:
        col1, col2, col3, col4 = st.columns(4)
        cols = [col1, col2, col3, col4]
        
        for i, code in enumerate(nordic_codes):
            row = df_nordic[df_nordic["country_code"] == code]
            with cols[i]:
                if not row.empty:
                    r = row.iloc[0]
                    st.metric(
                        code,
                        f"{int(r['total'])} medaljer",
                        f"🥇{int(r['gold'])} 🥈{int(r['silver'])} 🥉{int(r['bronze'])}"
                    )
                else:
                    st.metric(code, "0 medaljer", "Ingen medaljer")
    
    st.divider()
    
    # Per-Olympics breakdown
    st.subheader("📅 Per OL", anchor="per-ol")
    
    olympics_list = hist_data["olympics"]
    
    for _, ol in olympics_list.iterrows():
        year = ol["year"]
        city = ol["city"]
        
        with st.expander(f"**{year} {city}**", expanded=(year == 2022)):
            # Get medals for this Olympics
            df_ol = hist_data["medals"][hist_data["medals"]["year"] == year].copy()
            
            # Top 10
            df_top10 = df_ol.head(10)[["rank", "country_code", "gold", "silver", "bronze", "total"]].copy()
            df_top10.columns = ["Rank", "Land", "🥇", "🥈", "🥉", "Total"]
            
            st.dataframe(df_top10, use_container_width=True, hide_index=True)
            
            # Nordic countries in this Olympics
            df_nordic_ol = df_ol[df_ol["country_code"].isin(nordic_codes)]
            if not df_nordic_ol.empty:
                st.markdown("**Nordiske land:**")
                for _, r in df_nordic_ol.iterrows():
                    st.markdown(f"- **{r['country_code']}**: Rank {r['rank']} - {r['gold']}G {r['silver']}S {r['bronze']}B = {r['total']} medaljer")
    
    st.divider()
    
    # Trend chart for Norway
    st.subheader("📈 Norges utvikling", anchor="norges-utvikling")
    
    df_nor = hist_data["medals"][hist_data["medals"]["country_code"] == "NOR"].copy()
    df_nor = df_nor.sort_values("year")
    
    if not df_nor.empty:
        df_chart = df_nor.set_index("year")[["gold", "silver", "bronze"]]
        st.bar_chart(df_chart)
        st.caption("Norges medaljer per OL (2010-2022)")


# ============================================================
# PAGE: PREDIKASJON OVERSIKT
# ============================================================
elif page == "Predikasjon oversikt":
    st.header("🏆 Predikasjon oversikt", anchor="predikasjon-oversikt")
    
    df_pred = load_predictions()
    
    if df_pred is None:
        st.error("Ingen prediksjoner funnet.")
        st.info("Kjør `python predict.py` for å generere prediksjoner.")
        st.stop()
    
    # Summary metrics
    st.subheader("Topp 10 Land", anchor="topp-10-land")
    
    df_top10 = df_pred.head(10).copy()
    
    # Display as table with medal emojis and G/B ratio
    df_display = df_top10.copy()
    
    # Calculate G/B ratio before renaming columns
    df_display["G/B"] = df_display.apply(
        lambda r: f"{float(r['gold'])/max(float(r['bronze']), 0.1):.2f}", axis=1
    )
    
    df_display = df_display[["country", "gold", "silver", "bronze", "total", "G/B"]]
    df_display.columns = ["Land", "🥇 Gull", "🥈 Sølv", "🥉 Bronse", "Total", "G/B"]
    df_display.index = range(1, len(df_display) + 1)
    df_display.index.name = "Rank"
    
    # Format numbers with 1 decimal
    for col in ["🥇 Gull", "🥈 Sølv", "🥉 Bronse", "Total"]:
        df_display[col] = df_display[col].apply(lambda x: f"{float(x):.1f}")
    
    st.dataframe(df_display, use_container_width=True)
    
    st.caption("G/B = Gull/Bronse ratio. >1.0 = flere gull enn bronse (dominans), <1.0 = flere bronse (dybde)")
    
    st.divider()
    
    # Nordic countries detail
    st.subheader("Nordiske land", anchor="nordiske-land-pred")
    
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
    st.subheader("Medaljefordeling - Topp 15", anchor="medaljefordeling")
    
    df_chart = df_pred.head(15).set_index("country")[["gold", "silver", "bronze"]]
    st.bar_chart(df_chart)
    
    st.divider()
    
    # Full table
    st.subheader("Alle land", anchor="alle-land")
    st.dataframe(df_pred, use_container_width=True, hide_index=True)


# ============================================================
# PAGE: DRILLDOWN
# ============================================================
elif page == "Drilldown":
    st.header("🔍 Drilldown", anchor="drilldown")
    
    df_comp = load_competition_predictions()
    
    if df_comp is None:
        st.error("Ingen konkurranseprediksjoner funnet.")
        st.info("Kjør `python predict.py` for å generere prediksjoner.")
        st.stop()
    
    # Two tabs: Athlete and Sport
    tab_athlete, tab_sport = st.tabs(["Per utøver", "Per sport"])
    
    # --------------------------------------------------------
    # TAB: Per utøver
    # --------------------------------------------------------
    with tab_athlete:
        st.subheader("🏃 Utøver-drilldown", anchor="utover-drilldown")
        st.caption("Velg en utøver for å se alle konkurranser de kan ta medalje i.")
        
        # Get unique athletes with their countries
        athletes_list = df_comp[["athlete_name", "country"]].drop_duplicates()
        athletes_list = athletes_list.sort_values("athlete_name")
        athletes_list["display"] = athletes_list["athlete_name"] + " (" + athletes_list["country"] + ")"
        
        # Country filter first
        countries = sorted(df_comp["country"].unique())
        selected_country = st.selectbox(
            "Filtrer etter land",
            ["Alle"] + countries,
            key="athlete_country_filter"
        )
        
        if selected_country != "Alle":
            athletes_filtered = athletes_list[athletes_list["country"] == selected_country]
        else:
            athletes_filtered = athletes_list
        
        # Athlete selector
        selected_athlete_display = st.selectbox(
            "Velg utøver",
            athletes_filtered["display"].tolist(),
            key="athlete_selector"
        )
        
        if selected_athlete_display:
            # Extract athlete name
            selected_athlete = selected_athlete_display.rsplit(" (", 1)[0]
            
            # Get all competitions for this athlete
            df_athlete = df_comp[df_comp["athlete_name"] == selected_athlete].copy()
            
            # Sort by medal probability
            df_athlete = df_athlete.sort_values("medal_prob", ascending=False)
            
            # Format probabilities
            df_athlete["Gull %"] = (df_athlete["gold_prob"] * 100).round(1)
            df_athlete["Sølv %"] = (df_athlete["silver_prob"] * 100).round(1)
            df_athlete["Bronse %"] = (df_athlete["bronze_prob"] * 100).round(1)
            df_athlete["Medalje %"] = (df_athlete["medal_prob"] * 100).round(1)
            
            # Display
            st.markdown(f"### {selected_athlete}")
            
            # Summary metrics
            total_medal_prob = df_athlete["medal_prob"].sum()
            expected_golds = df_athlete["gold_prob"].sum()
            num_competitions = len(df_athlete)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Konkurranser", num_competitions)
            col2.metric("Forventet gull", f"{expected_golds:.1f}")
            col3.metric("Forventet medaljer", f"{total_medal_prob:.1f}")
            
            st.divider()
            
            # Table with all competitions
            df_show = df_athlete[["competition", "Gull %", "Sølv %", "Bronse %", "Medalje %"]].copy()
            df_show.columns = ["Konkurranse", "🥇 Gull %", "🥈 Sølv %", "🥉 Bronse %", "Medalje %"]
            
            st.dataframe(df_show, use_container_width=True, hide_index=True)
    
    # --------------------------------------------------------
    # TAB: Per sport
    # --------------------------------------------------------
    with tab_sport:
        st.subheader("🎿 Sport-drilldown", anchor="sport-drilldown")
        st.caption("Velg en sport for å se alle konkurranser og medaljekandidater.")
        
        # Get sports from database
        conn = get_connection()
        df_sports = pd.read_sql_query("""
            SELECT DISTINCT s.name as sport, c.name as competition, c.id as comp_id
            FROM competitions c
            JOIN sports s ON c.sport_id = s.id
            ORDER BY s.name, c.name
        """, conn)
        conn.close()
        
        # Sport selector
        sports = sorted(df_sports["sport"].unique())
        selected_sport = st.selectbox(
            "Velg sport",
            sports,
            key="sport_selector"
        )
        
        if selected_sport:
            # Get competitions for this sport
            sport_competitions = df_sports[df_sports["sport"] == selected_sport]["competition"].tolist()
            
            st.markdown(f"### {selected_sport}")
            st.markdown(f"**{len(sport_competitions)} konkurranser**")
            
            st.divider()
            
            # Show each competition with top contenders
            for comp_name in sport_competitions:
                # Get predictions for this competition
                df_comp_filtered = df_comp[df_comp["competition"] == comp_name].copy()
                
                if df_comp_filtered.empty:
                    st.markdown(f"**{comp_name}** - Ingen data")
                    continue
                
                # Sort by medal probability
                df_comp_filtered = df_comp_filtered.sort_values("gold_prob", ascending=False)
                
                # Get top 5
                top5 = df_comp_filtered.head(5)
                
                # Format
                top5["Gull %"] = (top5["gold_prob"] * 100).round(1)
                top5["Medalje %"] = (top5["medal_prob"] * 100).round(1)
                
                # Display as expander
                with st.expander(f"**{comp_name}**", expanded=False):
                    df_show = top5[["athlete_name", "country", "Gull %", "Medalje %"]].copy()
                    df_show.columns = ["Utøver", "Land", "🥇 Gull %", "Medalje %"]
                    st.dataframe(df_show, use_container_width=True, hide_index=True)


# ============================================================
# FOOTER
# ============================================================
st.sidebar.divider()
st.sidebar.markdown("""
**Data Pipeline**
- ISU API (skøyter)
- FIS Scraping (alpint, langrenn)
- Historiske OL-data (2010-2022)
- Legacy JSON (resten)

*Plackett-Luce Monte Carlo*
""")
