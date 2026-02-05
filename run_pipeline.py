#!/usr/bin/env python3
"""
Data Pipeline Runner

Orchestrates the data import from various sources:
1. Legacy JSON data (baseline)
2. ISU Speed Skating API (event-specific)
3. FIS Alpine Scraping (discipline-specific)
4. FIS Cross-Country Scraping (sprint vs distance)
5. Historical Olympics data (medal tables from last 4 games)

Usage:
    python run_pipeline.py           # Run all pipelines
    python run_pipeline.py legacy    # Only legacy import
    python run_pipeline.py isu       # Only ISU import
    python run_pipeline.py fis       # Only FIS Alpine import
    python run_pipeline.py xc        # Only FIS Cross-Country import
    python run_pipeline.py hist      # Only historical Olympics import
"""

import sys

from database import init_db, get_stats
from pipelines.import_legacy import import_legacy_data


def run_all():
    """Run all pipelines in order."""
    print("=" * 60)
    print("DATA PIPELINE")
    print("=" * 60)
    
    # Step 1: Initialize database
    print("\n[1/6] Initializing database...")
    init_db()
    
    # Step 2: Import legacy data
    print("\n[2/6] Importing legacy data...")
    import_legacy_data()
    
    # Step 3: ISU Speed Skating API
    print("\n[3/6] Checking ISU API...")
    try:
        from pipelines.isu_speed_skating import test_api_connection, import_isu_data
        if test_api_connection():
            import_isu_data()
        else:
            print("  Skipping ISU import (API not accessible)")
    except Exception as e:
        print(f"  Skipping ISU import: {e}")
    
    # Step 4: FIS Alpine Skiing
    print("\n[4/6] Fetching FIS Alpine data...")
    try:
        from pipelines.fis_alpine import test_scraping, import_fis_alpine_data
        if test_scraping():
            import_fis_alpine_data()
        else:
            print("  Skipping FIS Alpine import (scraping failed)")
    except Exception as e:
        print(f"  Skipping FIS Alpine import: {e}")
    
    # Step 5: FIS Cross-Country Skiing
    print("\n[5/6] Fetching FIS Cross-Country data...")
    try:
        from pipelines.fis_cross_country import test_scraping as test_xc, import_fis_cross_country_data
        if test_xc():
            import_fis_cross_country_data()
        else:
            print("  Skipping FIS XC import (scraping failed)")
    except Exception as e:
        print(f"  Skipping FIS XC import: {e}")
    
    # Step 6: Historical Olympics Data
    print("\n[6/6] Importing historical Olympics data...")
    try:
        from pipelines.import_historical import import_historical_data
        import_historical_data()
    except Exception as e:
        print(f"  Skipping historical import: {e}")
    
    # Final stats
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    
    stats = get_stats()
    print("\nDatabase statistics:")
    print(f"  Countries:    {stats['countries']}")
    print(f"  Sports:       {stats['sports']}")
    print(f"  Competitions: {stats['competitions']}")
    print(f"  Athletes:     {stats['athletes']}")
    print(f"  Entries:      {stats['entries']}")
    print(f"  Excluded:     {stats['excluded_athletes']}")
    print(f"\n  Entries by source: {stats['entries_by_source']}")


def run_legacy_only():
    """Run only legacy import."""
    init_db()
    import_legacy_data()


def run_isu_only():
    """Run only ISU import."""
    from pipelines.isu_speed_skating import test_api_connection, import_isu_data
    if test_api_connection():
        import_isu_data()


def run_fis_only():
    """Run only FIS Alpine import."""
    from pipelines.fis_alpine import test_scraping, import_fis_alpine_data
    if test_scraping():
        import_fis_alpine_data()


def run_xc_only():
    """Run only FIS Cross-Country import."""
    from pipelines.fis_cross_country import test_scraping, import_fis_cross_country_data
    if test_scraping():
        import_fis_cross_country_data()


def run_historical_only():
    """Run only historical Olympics import."""
    from pipelines.import_historical import import_historical_data
    import_historical_data()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "legacy":
            run_legacy_only()
        elif cmd == "isu":
            run_isu_only()
        elif cmd == "fis":
            run_fis_only()
        elif cmd == "xc":
            run_xc_only()
        elif cmd == "hist":
            run_historical_only()
        else:
            print(f"Unknown command: {cmd}")
            print("Usage: python run_pipeline.py [legacy|isu|fis|xc|hist]")
    else:
        run_all()
