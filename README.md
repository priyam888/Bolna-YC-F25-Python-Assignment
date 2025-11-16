# Bolna-YC-F25-Python-Assignment



#  OpenAI Status Monitor (Event-Driven RSS Listener)

A lightweight, event-driven Python tool that automatically listens for **live incident alerts** from the official OpenAI Status Page — without inefficient polling or scraping.

This project is designed to:
- Detect new outages/incidents / degraded performance
- Extract affected products automatically
- Log updates to JSON for historical tracking
- Run efficiently using the official RSS feed
- Demonstrate scalable architecture suitable for 100+ providers

 Built as an industry-style solution for interviews and real-world ops automation.

---

## Features
 Event-based incident monitoring (no HTML scraping)  
 Uses official status feed (RSS) — no hacks  
 Automatic product/service detection (Chat Completions, Assistants API, etc.)  
 JSON logging — maintain full incident history  
 Lightweight, fast, resource-efficient  
 Can be extended to multiple providers easily  
 No database required  
 No UI needed — logs directly to console  

---

##  Tech Stack
| Component | Choice |
|-----------|--------|
| Language | Python 3.8+ |
| Feed Parsing | feedparser |
| Timestamp Parsing | python-dateutil |
| Logging | JSON file |

---


```bash
git clone https://github.com/YOUR_USERNAME/openai-status-monitor.git
cd openai-status-monitor
