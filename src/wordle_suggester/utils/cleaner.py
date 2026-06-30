from pathlib import Path

def cleanup_old_logs(log_dir: Path, max_files: int = 10):
    logs = sorted(log_dir.glob("*.log"), key=lambda x: x.stat().st_mtime)
    
    while len(logs) >= max_files:
        oldest_log = logs.pop(0)
        oldest_log.unlink()