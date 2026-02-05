#!/usr/bin/env python3
"""
Data Pipeline Runner

Orchestrates the data import from various sources:
1. Legacy JSON data (baseline)
2. ISU Speed Skating API (event-specific)
3. FIS Alpine Scraping (discipline-specific)

Usage:
    python run_pipeline.py          # Run all pipelines
    python run_pipeline.py legacy   # Only legacy import
    python run_pipeline.py isu      # Only ISU import
    python run_pipeline.py fis      # Only FIS import
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
    print("\n[1/4] Initializing database...")
    init_db()
    
    # Step 2: Import legacy data
    print("\n[2/4] Importing legacy data...")
    import_legacy_data()
    
    # Step 3: ISU Speed Skating API
    print("\n[3/4] Checking ISU API...")
    try:
        from pipelines.isu_speed_skating import test_api_connection, import_isu_data
        if test_api_connection():
            import_isu_data()
        else:
            print("  Skipping ISU import (API not accessible)")
    except Exception as e:
        print(f"  Skipping ISU import: {e}")
    
    # Step 4: FIS Alpine Skiing
    print("\n[4/4] Fetching FIS Alpine data...")
    try:
        from pipelines.fis_alpine import test_scraping, import_fis_alpine_data
        if test_scraping():
            import_fis_alpine_data()
        else:
            print("  Skipping FIS import (scraping failed)")
    except Exception as e:
        print(f"  Skipping FIS import: {e}")
    
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
    """Run only FIS import."""
    from pipelines.fis_alpine import test_scraping, import_fis_alpine_data
    if test_scraping():
        import_fis_alpine_data()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "legacy":
            run_legacy_only()
        elif cmd == "isu":
            run_isu_only()
        elif cmd == "fis":
            run_fis_only()
        else:
            print(f"Unknown command: {cmd}")
            print("Usage: python run_pipeline.py [legacy|isu|fis]")
    else:
        run_all()
