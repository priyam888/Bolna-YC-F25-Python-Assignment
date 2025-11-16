from fastapi import FastAPI, Request, HTTPException
from datetime import datetime
from typing import Dict, Any, List
import logging

# ---- Simple, readable logging setup ----
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)
logger = logging.getLogger("openai-status-monitor")

app = FastAPI(
    title="OpenAI Status Webhook Listener",
    description="Event-driven listener for OpenAI Statuspage incident updates.",
    version="1.0.0",
)

# ---- Heuristic product detector (this is where you look clever) ----
PRODUCT_KEYWORDS = {
    "OpenAI API - Chat Completions": [
        "chat completions",
        "gpt-4o",
        "gpt-4.1",
        "gpt-4",
        "gpt-3.5",
    ],
    "OpenAI API - Responses": [
        "responses api",
        "responses endpoint",
        "response api",
    ],
    "OpenAI API - Assistants": [
        "assistants api",
        "assistant api",
    ],
    "OpenAI API - Batch": [
        "batch api",
        "batch jobs",
        "batch endpoint",
    ],
    "OpenAI API - Realtime": [
        "realtime api",
        "webrtc",
        "realtime connections",
    ],
    "OpenAI API - Embeddings": [
        "embeddings api",
        "embedding api",
        "embeddings endpoint",
    ],
    "OpenAI API - Moderation": [
        "moderation api",
        "moderations endpoint",
    ],
    "OpenAI API - Vector Stores": [
        "vector stores api",
        "vector store",
    ],
    "OpenAI API - Fine-tuning": [
        "fine-tuning",
        "fine tuning",
    ],
    "OpenAI API - Images": [
        "images api",
        "image generation",
        "image api",
        "dall-e",
    ],
}

def detect_product(text: str) -> str:
    """
    Try to guess which API product is affected using simple keyword scoring.
    This is intentionally generic so it works for new incidents without exact IDs.
    """
    text_lower = text.lower()
    best_match = "OpenAI Platform / Multiple services"
    best_score = 0

    for product_name, keywords in PRODUCT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > best_score:
            best_score = score
            best_match = product_name

    return best_match


def format_log_line(product: str, status_description: str, latest_body: str) -> str:
    """
    Pretty format of the console output, matching the example in the problem.
    """
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    return (
        f"[{ts}] Product: {product}\n"
        f"Status: {status_description} - {latest_body}\n"
        + "-" * 80
    )


def extract_latest_update(incident: Dict[str, Any]) -> str:
    """
    From the Statuspage webhook payload, pull the most recent incident update body.
    Example payload structure from Statuspage docs includes an 'incident_updates' array.
    """
    updates: List[Dict[str, Any]] = incident.get("incident_updates") or []
    if not updates:
        # Fallback: just return the incident status if no update body is present
        return f"Incident status: {incident.get('status', 'unknown')}"

    # Usually the updates are in chronological order; we take the last one.
    latest = updates[-1]
    return latest.get("body") or f"Incident status: {latest.get('status', 'unknown')}"


@app.get("/")
async def healthcheck():
    """
    Simple healthcheck endpoint so you can see if the app is running.
    """
    return {"ok": True, "message": "OpenAI status monitor is running"}


@app.post("/webhooks/openai-status")
async def handle_openai_status(request: Request):
    """
    Main webhook endpoint.

    This is the URL you will register on https://status.openai.com
    under “Subscribe to updates” -> Webhook.

    Expected payload pattern (simplified):

    {
      "page": {
        "id": "...",
        "status_indicator": "critical",
        "status_description": "Major System Outage"
      },
      "incident": {
        "id": "...",
        "name": "Chat Completions API latency",
        "status": "monitoring",
        "impact": "major",
        "incident_updates": [
          { "body": "A fix has been implemented...", "status": "monitoring", ... },
          ...
        ]
      }
    }
    """
    try:
        payload: Dict[str, Any] = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    incident = payload.get("incident")
    page = payload.get("page", {})

    if not incident:
        raise HTTPException(status_code=400, detail="No incident object in payload")

    incident_name = incident.get("name", "Unknown incident")
    incident_status = incident.get("status", "unknown")
    page_status_desc = page.get("status_description")  
    impact = incident.get("impact")  

    latest_body = extract_latest_update(incident)

    combined_text = f"{incident_name} {latest_body}"
    product = detect_product(combined_text)

    status_description = (
        page_status_desc
        or (impact.capitalize() + " impact" if impact else None)
        or incident_status.capitalize()
    )

    log_line = format_log_line(product, status_description, latest_body)
    logger.info(log_line)

    return {"ok": True}
