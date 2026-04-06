from pathlib import Path
from datetime import datetime
import json
import secrets


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

def serialize(obj):
    """JSON serializer for objects not serializable by default."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def log_entry(
        agent_name,
        system_prompt,
        model_name,
        question,
        answer,
        search_results,
        source):
    """Create a log entry for an agent interaction."""
    return {
        "agent_name": agent_name,
        "system_prompt": system_prompt,
        "model_name": model_name,
        "question": question,
        "answer": answer,
        "search_results": search_results,
        "source": source,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

def log_interaction_to_file(entry):
    """"Log an agent interaction to a JSON file with a unique timestamped filename."""
    ts = entry['timestamp']
    ts_obj = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    ts_str = ts_obj.strftime("%Y%m%d_%H%M%S")
    rand_hex = secrets.token_hex(3)

    filename = f"{entry['agent_name']}_{ts_str}_{rand_hex}.json"
    with open(LOG_DIR / filename, "w", encoding="utf-8") as f_out:
        json.dump(entry, f_out, indent=2, ensure_ascii=False, default=serialize)
    
    return LOG_DIR / filename
