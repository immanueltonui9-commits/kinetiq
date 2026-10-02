# Kinetiq — AI Automation Landing Page + Waitlist

A zero-dependency MVP you can run locally with Python 3.

## Run it

```bash
python server.py
```

Open http://localhost:8000

Waitlist submissions are stored in `data/waitlist.csv`.

## What is included

- Responsive landing page
- Company name + positioning: **Kinetiq**
- Hero, use cases, process, private-beta section
- Functional waitlist form
- Basic validation + duplicate-email handling
- `/health` endpoint
- `/admin/waitlist-count` endpoint

## Production checklist

Before public launch, replace CSV storage with a managed database/email provider, add rate limiting + CAPTCHA/abuse protection, publish a real privacy policy/terms, and configure HTTPS. Do not expose raw waitlist data through a public admin endpoint.

## OpenAI integration

The landing page is provider-neutral by design, but the intended product architecture is to use OpenAI's Responses API for the AI layer. OpenAI's current docs show direct model requests through `POST /v1/responses` and the official Python SDK via `client.responses.create(...)`.

Keep your API key on the server, never in browser JavaScript.
