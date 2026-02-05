#!/usr/bin/env python3
"""
V2 Data Pipeline Runner

Orchestrates the data import from various sources:
1. Legacy JSON data (baseline)
2. ISU Speed Skating API (event-specific)
3. IBU Biathlon API (future)

Usage:
    python run_pipeline.py          # Run all pipelines
    python run_pipeline.py legacy   # Only legacy import
    python run_pipeline.py isu      # Only ISU import
"""

import sys
from pathlib import Path

# Add v2 to path
sys.path.insert(0, str(Path(__file__).parent))

from database import init_db, get_stats
from pipelines.import_legacy import import_legacy_data


def run_all():
    """Run all pipelines in order."""
    print("=" * 60)
    print("V2 DATA PIPELINE")
    print("=" * 60)
    
    # Step 1: Initialize database
    print("\n[1/3] Initializing database...")
    init_db()
    
    # Step 2: Import legacy data
    print("\n[2/3] Importing legacy data...")
    import_legacy_data()
    
    # Step 3: Try ISU API (may fail without network)
    print("\n[3/3] Checking ISU API...")
    try:
        from pipelines.isu_speed_skating import test_api_connection, import_isu_data
        if test_api_connection():
            import_isu_data()
        else:
            print("  Skipping ISU import (API not accessible)")
    except Exception as e:
        print(f"  Skipping ISU import: {e}")
    
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


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "legacy":
            run_legacy_only()
        elif cmd == "isu":
            run_isu_only()
        else:
            print(f"Unknown command: {cmd}")
            print("Usage: python run_pipeline.py [legacy|isu]")
    else:
        run_all()
