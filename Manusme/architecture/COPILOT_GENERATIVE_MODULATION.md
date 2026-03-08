# Architecture: Copilot Generative Modulation in WhatsApp

## 1. Overview

This document details the architecture where **Azure Copilot (Gen AI)** becomes a **generative layer** that actively **modulates** Azure Communication Services (ACS) AI capabilities directly within the **Meta WhatsApp Business Platform (WPP)**. Every interaction is anchored on the **Azure Blockchain** as an immutable record.

This is the core of the **Manusme** vision: a fully autonomous, generative, and auditable communication loop.

## 2. The Generative Loop

The architecture creates a closed, self-improving loop:

**Copilot (Gen AI) → ACS Azure (Modulation) → WhatsApp (Delivery) → Blockchain (Record) → Copilot (Learning)**

1.  **Copilot as the Generative Brain**: Copilot doesn't just respond; it proactively generates and modulates communication strategies based on real-time context and historical data from the blockchain.
2.  **ACS as the Modulation Layer**: ACS is no longer just a channel. It becomes the dynamic interface where Copilot's generative instructions are translated into concrete actions (e.g., sending a specific interactive message, changing the AI's tone, escalating to a human).
3.  **WhatsApp as the Delivery Channel**: The WPP is the high-fidelity endpoint where the modulated communication is delivered to the user.
4.  **Blockchain as the Immutable Record**: Every part of the loop—Copilot's decision, the ACS modulation, the user's response—is recorded on the blockchain, creating a perfect, auditable memory for the AI.

## 3. Architecture Diagram

```mermaid
graph TD
    subgraph Generative AI Core (Azure)
        A[Azure Copilot / GPT-4o] -- "1. Generates Strategy" --> B(ACS Modulation Engine);
    end

    subgraph Communication & Delivery
        B -- "2. Modulates & Executes" --> C{Meta WPP Cloud API};
        C -- "3. Delivers to User" --> D[WhatsApp User];
        D -- "4. User Responds" --> C;
    end

    subgraph Immutable Ledger (Azure)
        C -- "5. Anchors Interaction" --> E[Azure Blockchain Service];
        E -- "6. Provides Historical Context" --> A;
    end

    style A fill:#0078D4,stroke:#333,stroke-width:2px
    style B fill:#0078D4,stroke:#333,stroke-width:2px
    style C fill:#1877F2,stroke:#333,stroke-width:2px
    style D fill:#25D366,stroke:#333,stroke-width:2px
    style E fill:#0078D4,stroke:#333,stroke-width:2px
```

## 4. Component Breakdown

### 4.1. Azure Copilot (Generative Brain)

-   **Engine**: Azure OpenAI Service with a fine-tuned GPT-4o model.
-   **Function**: Proactively decides the *what*, *why*, and *how* of the communication. It doesn't just answer questions; it drives the conversation.
-   **Input**: Real-time user messages and historical context queried from the Azure Blockchain.
-   **Output**: A **Modulation Instruction Set (MIS)**, which is a JSON object detailing the exact action to be taken.

**Example Modulation Instruction Set (MIS):**

```json
{
  "interactionId": "msg_12345",
  "strategy": "proactive_upsell",
  "acs_modulation": {
    "type": "interactive_template",
    "template_name": "interplanetary_offer_q2",
    "components": [
      {"type": "header", "parameters": [{"type": "image", "image": {"link": "..."}}]}, 
      {"type": "body", "parameters": [{"type": "text", "text": "Alexandre"}]}
    ],
    "ai_tone": "enthusiastic",
    "escalation_policy": "on_negative_sentiment"
  },
  "blockchain_anchor": {
    "record_intent": true,
    "metadata": {"campaign": "q2_promo"}
  }
}
```

### 4.2. ACS Modulation Engine

-   **Engine**: An Azure Function App that acts as the orchestrator.
-   **Function**: Receives the MIS from Copilot and translates it into specific API calls to ACS and the blockchain smart contract.
-   **Logic**: It parses the `acs_modulation` block and constructs the appropriate API request for the Meta WPP via ACS.

### 4.3. Meta WPP & ACS

-   **Function**: The reliable, high-fidelity channel for message delivery and reception. ACS abstracts the complexity of the WPP API.

### 4.4. Azure Blockchain Service

-   **Function**: The immutable memory of the entire system.
-   **Smart Contract**: The `WhatsAppMessageLedger` contract is updated to store not just the message, but also the **Copilot MIS** that prompted it. This creates a complete, auditable link between AI intent and action.

**Updated `MessageRecord` struct in the smart contract:**

```solidity
struct MessageRecord {
    // ... (previous fields)
    string copilotStrategy;      // e.g., "proactive_upsell"
    string modulationInstruction; // The JSON string of the MIS
}
```

## 5. The Full Loop in Action

1.  **User**: 
