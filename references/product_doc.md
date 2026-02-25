# alittlebitofmoney.com — Product Reference

## What It Is

alittlebitofmoney.com is a pay-per-request proxy for OpenAI APIs using Bitcoin Lightning payments. No account signup, no API key management, no dashboard — just pay a Lightning invoice and make your API call.

## How It Works (L402 Flow)

1. Send a request to the proxy endpoint (same format as OpenAI API)
2. Receive a `402 Payment Required` response with a Lightning invoice
3. Pay the invoice with any Lightning wallet
4. Resend the request with the payment preimage as proof
5. Get the OpenAI API response

The Lightning preimage serves as both cryptographic proof of payment and bearer token.

## Key Value Props

- **No Account Needed** — No signup, no email, no dashboard
- **No API Key** — The payment preimage IS your access token
- **Pay Per Request** — Only pay for what you use, in satoshis
- **Privacy** — No identity tied to API calls
- **Agent-Friendly** — Autonomous AI agents can pay programmatically without human-managed credentials

## Example

```bash
# Step 1: Make a request, get an invoice
curl -X POST https://alittlebitofmoney.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "Hello"}]}'

# Response: 402 with Lightning invoice in header

# Step 2: Pay the invoice with any Lightning wallet

# Step 3: Resend with the preimage
curl -X POST https://alittlebitofmoney.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: L402 <preimage>" \
  -d '{"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "Hello"}]}'
```

## Pricing

Prices are denominated in satoshis (sats). Approximately ~50 sats per chat completion request (varies by model).

## Supported Endpoints

- Chat Completions (`/v1/chat/completions`)
- Image Generation
- Embeddings  
- Audio (TTS/STT)

## URL

https://alittlebitofmoney.com

## Technical Standard

Implements the L402 protocol — an HTTP 402-based authentication scheme using Lightning Network macaroons and preimages.

## Who It's For

- Developers who want quick, no-friction access to AI APIs
- AI agents that need to pay for services autonomously
- Privacy-conscious developers
- Developers in regions where OpenAI accounts are hard to get
- Anyone who wants to try an API call without creating yet another account
