# Archive Folder

This folder contains old scripts and files that are no longer needed for the main application workflow.

## Archived Files

### Debug/Test Scripts
- `debug_pipeline.py` - Old debugging script for testing pipeline
- `test_model.py` - Model testing script

### One-time Data Cleanup Scripts
- `clean_history.py` - Script to remove duplicate entries from history file (already executed)
- `convert_history.py` - Script to convert old data format to new format (already executed)

### Logs & Documentation
- `server.log` - Old server logs
- `tree.txt` - Directory structure snapshot

## Active Scripts (NOT in archive)

The following scripts are still actively used:
- `collect_all.py` - Master data collection script (runs all resource scrapers)
- `pipeline.py` - Main ML processing pipeline
- `server.py` - CORS-enabled HTTP server for serving JSON outputs
- `run_hourly.py` - Cron job script for hourly pipeline runs

## Note

These archived files are kept for reference only. They can be safely deleted if disk space is needed.
