# -*- coding: utf-8 -*-
"""Cliente OpenRouter para el chat con IA."""
import os
import json
import re
import time
import urllib.request
import urllib.error

def _clean_json(text):
    return re.sub(r"[\x00-\x1f]", " ", text)


API_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip()
BASE_URL = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
DEFAULT_MODEL = os.environ.get("OPENROUTER_MODEL", "baidu/ernie-5.5-flash-preview:free")
FALLBACKS = [m.strip() for m in os.environ.get(
    "OPENROUTER_FALLBACK_MODELS",
    "google/gemma-4-31b-it:free,google/gemma-4-26b-a4b-it:free,inclusionai/ling-3.2-flash:free,openrouter/free",
).split(",") if m.strip()]
REFERER = os.environ.get("OPENROUTER_REFERER", "http://localhost:8000")
TITLE = os.environ.get("OPENROUTER_TITLE", "Puerto A&M Demo")
TIMEOUT = int(os.environ.get("OPENROUTER_TIMEOUT", "45"))


def is_configured():
    return bool(API_KEY)


def _headers():
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "HTTP-Referer": REFERER,
        "X-Title": TITLE,
    }


def _extract(data):
    try:
        msg = data["choices"][0]["message"]
    except (KeyError, IndexError, TypeError):
        return None
    content = msg.get("content")
    if content:
        return content.strip()
    # algunos modelos reasoning devuelven solo reasoning
    reasoning = msg.get("reasoning") or msg.get("reasoning_details")
    if isinstance(reasoning, list):
        reasoning = "\n".join(str(x.get("text", x)) for x in reasoning)
    if reasoning:
        return str(reasoning).strip()
    return None


def chat(messages, model=None, temperature=0.3, max_tokens=600):
    if not API_KEY:
        return None
    models = [model] if model else []
    models += [DEFAULT_MODEL] + [m for m in FALLBACKS if m != DEFAULT_MODEL]
    # dedup
    seen = set()
    uniq = []
    for m in models:
        if m and m not in seen:
            seen.add(m); uniq.append(m)

    for m in uniq:
        payload = {
            "model": m,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(BASE_URL + "/chat/completions", data=data, headers=_headers(), method="POST")
        for attempt in range(2):
            try:
                with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                    raw = resp.read().decode("utf-8", errors="replace")
                    parsed = json.loads(_clean_json(raw), strict=False)
                    out = _extract(parsed)
                    if out:
                        return out
                    break
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8", errors="replace")
                # rate limit / unavailable: try next model
                if e.code in (429, 404, 502, 503, 504):
                    time.sleep(1)
                    break
                return None
            except Exception:
                time.sleep(1)
                break
    return None
