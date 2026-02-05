#!/usr/bin/env python3
"""
Streamlit app to inspect Olympic medal prediction data.

Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
OUTPUT_DIR = Path(__file__).parent / "output"
NORDIC_COUNTRIES = ["NOR", "SWE", "FIN", "DEN"]
COUNTRY_FLAGS = {"NOR": "🇳🇴", "SWE": "🇸🇪", "FIN": "🇫🇮", "DEN": "🇩🇰"}

st.set_page_config(
    page_title="Olympic Medal Prediction - Data Inspector",
    page_icon="🏅",
    layout="wide"
)

@st.cache_data
def load_data():
    """Load all data files."""
    with open(DATA_DIR / "sports.json") as f:
        sports = json.load(f)
    with open(DATA_DIR / "competitions.json") as f:
        competitions = json.load(f)
    with open(DATA_DIR / "athletes.json") as f:
        athletes = json.load(f)
    with open(DATA_DIR / "entries.json") as f:
        entries = json.load(f)
    return sports, competitions, athletes, entries


def main():
    st.title("🏅 Olympic Medal Prediction - Data Inspector")
    st.markdown("**2026 Winter Olympics - Milan Cortina**")
    
    # Load data
    sports, competitions, athletes, entries = load_data()
    
    # Convert to DataFrames
    df_sports = pd.DataFrame(sports)
    df_competitions = pd.DataFrame(competitions)
    df_athletes = pd.DataFrame(athletes)
    df_entries = pd.DataFrame(entries)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select page:",
        ["Overview", "Predictions", "Sports", "Competitions", "Athletes", "Entries", "Nordic Summary"]
    )
    
    # Overview page
    if page == "Overview":
        st.header("📊 Data Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Sports", len(sports))
        col2.metric("Competitions", len(competitions))
        col3.metric("Athletes", len(athletes))
        col4.metric("Entries", len(entries))
        
        st.divider()
        
        # Coverage analysis
        st.subheader("Data Coverage")
        
        comps_with_data = df_entries["competition_id"].nunique()
        coverage_pct = comps_with_data / len(competitions) * 100
        
        col1, col2 = st.columns(2)
        col1.metric("Competitions with athlete data", f"{comps_with_data} / {len(competitions)}")
        col2.metric("Coverage", f"{coverage_pct:.0f}%")
        
        # Missing competitions
        covered_comps = set(df_entries["competition_id"].unique())
        all_comps = set(df_competitions["id"])
        missing_comps = all_comps - covered_comps
        
        if missing_comps:
            with st.expander(f"Missing competitions ({len(missing_comps)})"):
                missing_df = df_competitions[df_competitions["id"].isin(missing_comps)][["id", "name", "sport_id", "gender"]]
                st.dataframe(missing_df, use_container_width=True)
        
        # Athletes by country
        st.subheader("Athletes by Country")
        country_counts = df_athletes["country"].value_counts().head(15)
        st.bar_chart(country_counts)
        
        # Nordic athletes
        nordic_athletes = df_athletes[df_athletes["country"].isin(NORDIC_COUNTRIES)]
        nordic_counts = nordic_athletes["country"].value_counts()
        
        st.subheader("Nordic Athletes")
        col1, col2, col3, col4 = st.columns(4)
        for col, country in zip([col1, col2, col3, col4], NORDIC_COUNTRIES):
            count = nordic_counts.get(country, 0)
            col.metric(country, count)
    
    # Predictions page
    elif page == "Predictions":
        st.header("🎯 Predictions")
        
        # Find all prediction files
        prediction_files = sorted(OUTPUT_DIR.glob("*.csv")) if OUTPUT_DIR.exists() else []
        
        if not prediction_files:
            st.warning("No prediction files found in /output directory")
            st.info("Run `python prediction/v1/predict.py` to generate predictions")
        else:
            # Select prediction version
            file_names = [f.stem for f in prediction_files]
            selected_file = st.selectbox("Select prediction version:", file_names)
            
            # Load selected prediction
            selected_path = OUTPUT_DIR / f"{selected_file}.csv"
            df_pred = pd.read_csv(selected_path)
            
            st.subheader("📊 Medal Predictions")
            
            # Display as formatted cards
            cols = st.columns(len(df_pred))
            for col, (_, row) in zip(cols, df_pred.iterrows()):
                country = row["country"]
                flag = COUNTRY_FLAGS.get(country, "🏳️")
                
                with col:
                    st.markdown(f"### {flag} {country}")
                    st.metric("🥇 Gold", f"{row['gold']:.0f}", delta=None)
                    st.metric("🥈 Silver", f"{row['silver']:.0f}", delta=None)
                    st.metric("🥉 Bronze", f"{row['bronze']:.0f}", delta=None)
                    st.metric("📊 Total", f"{row['total']:.0f}", delta=None)
            
            st.divider()
            
            # Show confidence intervals
            st.subheader("📈 Confidence Intervals (95%)")
            
            ci_data = []
            for _, row in df_pred.iterrows():
                ci_data.append({
                    "Country": row["country"],
                    "Gold": f"{row['gold']:.0f} ({row['gold_low']:.0f}-{row['gold_high']:.0f})",
                    "Silver": f"{row['silver']:.0f} ({row['silver_low']:.0f}-{row['silver_high']:.0f})",
                    "Bronze": f"{row['bronze']:.0f} ({row['bronze_low']:.0f}-{row['bronze_high']:.0f})",
                    "Total": f"{row['total']:.0f} ({row['total_low']:.0f}-{row['total_high']:.0f})",
                })
            
            st.dataframe(pd.DataFrame(ci_data), use_container_width=True, hide_index=True)
            
            st.divider()
            
            # Raw data
            with st.expander("📄 Raw prediction data"):
                st.dataframe(df_pred, use_container_width=True, hide_index=True)
            
            # Submission format
            st.subheader("📝 Submission Format")
            st.markdown("Copy this for the challenge submission:")
            
            submission = ""
            for _, row in df_pred.iterrows():
                country = row["country"]
                if country == "NOR":
                    name = "Norway"
                elif country == "SWE":
                    name = "Sweden"
                elif country == "FIN":
                    name = "Finland"
                elif country == "DEN":
                    name = "Denmark"
                else:
                    name = country
                
                g = int(round(row['gold']))
                s = int(round(row['silver']))
                b = int(round(row['bronze']))
                submission += f"{name}: 🥇 Gold – {g} 🥈 Silver – {s} 🥉 Bronze – {b}\n"
            
            st.code(submission, language=None)
    
    # Sports page
    elif page == "Sports":
        st.header("🎿 Sports")
        
        st.dataframe(
            df_sports[["id", "name", "events", "scoring_type", "federation", "data_source_url"]],
            use_container_width=True,
            hide_index=True
        )
        
        # Events per sport
        st.subheader("Events per Sport")
        events_chart = df_sports.set_index("name")["events"].sort_values(ascending=True)
        st.bar_chart(events_chart)
        
        total_events = df_sports["events"].sum()
        st.info(f"Total medal events: {total_events}")
    
    # Competitions page
    elif page == "Competitions":
        st.header("🏆 Competitions")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        sport_filter = col1.selectbox(
            "Filter by sport:",
            ["All"] + sorted(df_competitions["sport_id"].unique().tolist())
        )
        
        gender_filter = col2.selectbox(
            "Filter by gender:",
            ["All", "M", "F", "X"]
        )
        
        type_filter = col3.selectbox(
            "Filter by type:",
            ["All", "individual", "team"]
        )
        
        # Apply filters
        filtered = df_competitions.copy()
        if sport_filter != "All":
            filtered = filtered[filtered["sport_id"] == sport_filter]
        if gender_filter != "All":
            filtered = filtered[filtered["gender"] == gender_filter]
        if type_filter != "All":
            filtered = filtered[filtered["type"] == type_filter]
        
        st.dataframe(filtered, use_container_width=True, hide_index=True)
        st.caption(f"Showing {len(filtered)} competitions")
    
    # Athletes page
    elif page == "Athletes":
        st.header("👤 Athletes")
        
        # Filters
        col1, col2 = st.columns(2)
        
        countries = sorted(df_athletes["country"].unique().tolist())
        country_filter = col1.multiselect(
            "Filter by country:",
            countries,
            default=NORDIC_COUNTRIES
        )
        
        search = col2.text_input("Search by name:")
        
        # Apply filters
        filtered = df_athletes.copy()
        if country_filter:
            filtered = filtered[filtered["country"].isin(country_filter)]
        if search:
            filtered = filtered[filtered["name"].str.lower().str.contains(search.lower())]
        
        st.dataframe(filtered, use_container_width=True, hide_index=True)
        st.caption(f"Showing {len(filtered)} athletes")
    
    # Entries page
    elif page == "Entries":
        st.header("📝 Entries (Performance Data)")
        
        # Join with athlete and competition info
        df_entries_full = df_entries.merge(
            df_athletes[["id", "name", "country"]],
            left_on="athlete_id",
            right_on="id",
            suffixes=("", "_athlete")
        ).merge(
            df_competitions[["id", "name", "sport_id"]],
            left_on="competition_id",
            right_on="id",
            suffixes=("", "_competition")
        )
        
        df_entries_full = df_entries_full.rename(columns={
            "name": "athlete_name",
            "name_competition": "competition_name"
        })
        
        # Filters
        col1, col2 = st.columns(2)
        
        sport_filter = col1.selectbox(
            "Filter by sport:",
            ["All"] + sorted(df_entries_full["sport_id"].unique().tolist())
        )
        
        country_filter = col2.multiselect(
            "Filter by country:",
            sorted(df_entries_full["country"].unique().tolist()),
            default=NORDIC_COUNTRIES
        )
        
        # Apply filters
        filtered = df_entries_full.copy()
        if sport_filter != "All":
            filtered = filtered[filtered["sport_id"] == sport_filter]
        if country_filter:
            filtered = filtered[filtered["country"].isin(country_filter)]
        
        # Select columns to display
        display_cols = ["athlete_name", "country", "competition_name", "score", "source_date"]
        filtered = filtered[display_cols].sort_values(["competition_name", "score"], ascending=[True, False])
        
        st.dataframe(filtered, use_container_width=True, hide_index=True)
        st.caption(f"Showing {len(filtered)} entries")
    
    # Nordic Summary page
    elif page == "Nordic Summary":
        st.header("🇳🇴🇸🇪🇫🇮🇩🇰 Nordic Summary")
        
        # Join entries with athlete info
        df_entries_full = df_entries.merge(
            df_athletes[["id", "name", "country"]],
            left_on="athlete_id",
            right_on="id"
        ).merge(
            df_competitions[["id", "name", "sport_id"]],
            left_on="competition_id",
            right_on="id",
            suffixes=("", "_competition")
        )
        
        nordic_entries = df_entries_full[df_entries_full["country"].isin(NORDIC_COUNTRIES)]
        
        for country in NORDIC_COUNTRIES:
            country_data = nordic_entries[nordic_entries["country"] == country]
            athletes_in_country = df_athletes[df_athletes["country"] == country]
            
            if len(athletes_in_country) == 0:
                continue
            
            st.subheader(f"{country} - {len(athletes_in_country)} athletes")
            
            # Group by sport
            sport_summary = country_data.groupby("sport_id").agg({
                "athlete_id": "nunique",
                "score": "max"
            }).rename(columns={"athlete_id": "athletes", "score": "top_score"})
            
            if not sport_summary.empty:
                st.dataframe(sport_summary, use_container_width=True)
            
            # Top athletes by score
            with st.expander("Top athletes"):
                top_athletes = country_data.groupby(["name", "sport_id"])["score"].max().sort_values(ascending=False).head(10)
                st.dataframe(top_athletes.reset_index())
            
            st.divider()


if __name__ == "__main__":
    main()
