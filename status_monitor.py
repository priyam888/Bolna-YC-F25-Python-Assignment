import feedparser
import time
import json
import os
from datetime import datetime
from dateutil import parser

RSS_URL = "https://status.openai.com/history.rss"
LOG_FILE = "logs/openai_status_log.json"  # JSON log storage
last_seen = None

PRODUCT_KEYWORDS = {
    "Chat Completions API": [
        "chat completions", "gpt-4", "gpt-4o", "gpt-3.5", "chatgpt"
    ],
    "Responses API": [
        "responses api", "response endpoint"
    ],
    "Assistants API": [
        "assistants api", "assistant"
    ],
    "Batch API": [
        "batch api", "batch job"
    ],
    "Realtime API": [
        "realtime api", "realtime"
    ],
    "Embeddings API": [
        "embedding", "embeddings"
    ],
    "Moderation API": [
        "moderation", "moderate"
    ],
    "Vector Stores API": [
        "vector store", "vector database"
    ],
    "Fine-tuning API": [
        "fine-tune", "fine tuning"
    ],
    "Image Generation API": [
        "image", "dall-e"
    ],
}


def detect_product(text: str) -> str:
    """Smart keyword-based service detection."""
    text_lower = text.lower()
    best_match = "OpenAI Platform / Multiple Services"
    best_score = 0

    for product, keywords in PRODUCT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > best_score:
            best_score = score
            best_match = product

    return best_match


# === JSON LOGGING ===
def log_to_json(data: dict):
    os.makedirs("logs", exist_ok=True)

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            json.dump([], f, indent=2)

    with open(LOG_FILE, "r") as f:
        existing = json.load(f)

    existing.append(data)

    with open(LOG_FILE, "w") as f:
        json.dump(existing, f, indent=2)


def format_timestamp(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def print_incident(entry):
    timestamp = parser.parse(entry.published)
    human_time = format_timestamp(timestamp)

    product = detect_product(entry.title + " " + entry.summary)

    print(f"[{human_time}] 🔔 NEW INCIDENT DETECTED")
    print(f"Product: {product}")
    print(f"Event: {entry.title}")
    print(f"Status: {entry.summary}")
    print("-" * 80)

    log_data = {
        "timestamp": human_time,
        "product": product,
        "event": entry.title,
        "status": entry.summary,
    }
    log_to_json(log_data)


# === MAIN MONITOR LOOP ===
def track_status():
    global last_seen
    print("🔍 Monitoring OpenAI Status via RSS...")
    print("Logs at:", LOG_FILE)
    print("Press Ctrl+C to stop\n")

    while True:
        feed = feedparser.parse(RSS_URL)
        if not feed.entries:
            print("⚠ Feed empty, retrying...")
            time.sleep(30)
            continue

        newest = feed.entries[0]
        timestamp = parser.parse(newest.published)

        if last_seen is None:
            last_seen = timestamp
            print("Initialized. Waiting for future updates...\n")
        else:
            if timestamp > last_seen:
                print_incident(newest)
                last_seen = timestamp

        time.sleep(30)


if __name__ == "__main__":
    track_status()
