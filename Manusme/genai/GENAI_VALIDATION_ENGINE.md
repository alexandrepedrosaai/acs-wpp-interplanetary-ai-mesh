# Gen AI Validation Engine for Meta WhatsApp + Azure Blockchain

## Overview

The **Gen AI Validation Engine** is the intelligence layer of the Manusme integration. It processes every WhatsApp message received via the Meta WPP Cloud API, performs multi-dimensional AI analysis, and reports the results back to the `WhatsAppMessageLedger` smart contract via the `AIValidationOracle`.

This engine runs as a set of **Azure Functions** backed by **Azure OpenAI (GPT-4o)** and **Azure AI Content Safety**, ensuring real-time, scalable validation.

## Validation Pipeline

Every incoming WhatsApp message passes through the following pipeline before being considered validated on the blockchain:

| Step | Service | Purpose |
|------|---------|---------|
| 1. Receive | ACS Webhook / Azure Function | Ingest message from Meta WPP Cloud API |
| 2. Content Safety | Azure AI Content Safety | Detect hate, violence, self-harm, sexual content |
| 3. Sentiment Analysis | Azure OpenAI (GPT-4o) | Understand user intent and emotional state |
| 4. Compliance Check | Azure OpenAI (GPT-4o) | Validate against business and regulatory policies |
| 5. Threat Detection | Azure AI + Custom Model | Identify phishing, spam, and social engineering |
| 6. Score & Flag | Aggregation Logic | Produce a final validation score (0–100) |
| 7. Oracle Report | Smart Contract Call | Write results to `WhatsAppMessageLedger` on-chain |

## Validation Score Interpretation

The engine produces a single score from 0 to 100 representing the trustworthiness of the message:

| Score Range | Status | Action |
|-------------|--------|--------|
| 90 – 100 | Trusted | Deliver immediately; anchor to blockchain |
| 70 – 89 | Low Risk | Deliver; flag for periodic review |
| 40 – 69 | Moderate Risk | Deliver with warning; trigger human review |
| 10 – 39 | High Risk | Hold for mandatory human review |
| 0 – 9 | Threat Detected | Block; alert security team; record on blockchain |

## Architecture Diagram

```
Meta WPP Cloud API
        │
        ▼
 ACS Webhook (Azure Function)
        │
        ├──────────────────────────────────┐
        ▼                                  ▼
Azure AI Content Safety          Azure OpenAI (GPT-4o)
  (Harm Detection)              (Sentiment + Compliance)
        │                                  │
        └──────────────┬───────────────────┘
                       ▼
              Score Aggregator
                       │
                       ▼
          AIValidationOracle (Azure Function)
                       │
                       ▼
     WhatsAppMessageLedger (Smart Contract)
                       │
                       ▼
           Azure Blockchain (Immutable Record)
```

## Integration with Meta WPP

The engine is registered as the **webhook URL** in the Meta for Developers App Dashboard. Meta sends all incoming messages, delivery receipts, and read receipts to this endpoint.

### Webhook Verification

Meta requires webhook verification via a `GET` request with a `hub.challenge` parameter. The Azure Function handles this automatically.

### Supported Message Types

The Gen AI Validation Engine supports all WhatsApp message types:

- **Text**: Full NLP analysis via Azure OpenAI
- **Image / Video / Audio**: Multimodal analysis via Azure AI Vision and Speech
- **Document**: Content extraction and analysis via Azure AI Document Intelligence
- **Interactive (Buttons / Lists)**: Intent classification via Azure OpenAI
- **Location**: Geospatial context analysis
- **Contacts**: Identity validation

## Key Design Principles

**Privacy by Design**: Message content is hashed before being stored on the blockchain. The Gen AI engine processes content in memory and does not persist raw message bodies.

**Auditability**: Every AI decision (score, flags, model used) is recorded on the blockchain via the `AIValidationOracle`, creating a transparent and auditable AI decision trail.

**Resilience**: The engine is deployed as a stateless Azure Function with auto-scaling, ensuring it can handle high message volumes without degradation.

**Human-in-the-Loop**: For messages scoring below 40, the engine automatically creates a task in Azure DevOps or Microsoft Teams for human review before delivery.

---

**Author**: Alexandre Pedrosa, EVP Multimodal AI Engineer at Meta and Microsoft Azure
