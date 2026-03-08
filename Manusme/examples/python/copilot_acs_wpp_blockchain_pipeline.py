"""
Manusme Pipeline: Copilot (Gen AI) → ACS Azure → Meta WhatsApp → Azure Blockchain
Author: Alexandre Pedrosa — EVP Multimodal AI Engineer at Meta and Microsoft Azure
© 2025-2026 Alexandre Pedrosa. All Rights Reserved.

This module implements the full generative communication loop:
  1. Azure Copilot (GPT-4o) generates a Modulation Instruction Set (MIS)
  2. ACS Modulation Engine translates MIS into a WhatsApp action
  3. Meta WPP Cloud API delivers the message to the user
  4. Azure Blockchain anchors the entire interaction as an immutable record
"""

import os
import json
import hashlib
from openai import AzureOpenAI
from azure.communication.messages import NotificationMessagesClient
from azure.communication.messages.models import (
    TextNotificationContent,
    TemplateNotificationContent,
    MessageTemplate,
    MessageTemplateText,
)
from web3 import Web3


# =============================================================================
# CONFIGURATION
# =============================================================================

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY  = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_MODEL    = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

ACS_CONNECTION_STRING = os.getenv("ACS_CONNECTION_STRING")
WPP_CHANNEL_ID        = os.getenv("WPP_CHANNEL_ID")

BLOCKCHAIN_NODE_URL   = os.getenv("AZURE_BLOCKCHAIN_NODE_URL")
LEDGER_CONTRACT_ADDR  = os.getenv("LEDGER_CONTRACT_ADDRESS")
LEDGER_CONTRACT_ABI   = json.loads(os.getenv("LEDGER_CONTRACT_ABI", "[]"))


# =============================================================================
# STEP 1 — COPILOT: Generate Modulation Instruction Set (MIS)
# =============================================================================

def copilot_generate_mis(user_message: str, user_number: str, history: list) -> dict:
    """
    Azure Copilot (GPT-4o) analyses the incoming WhatsApp message and generates
    a Modulation Instruction Set (MIS) that drives the ACS response.

    Args:
        user_message: The raw text received from the WhatsApp user.
        user_number:  The sender's WhatsApp number.
        history:      Previous interactions retrieved from the blockchain.

    Returns:
        A dict representing the MIS (strategy, message, tone, escalation policy).
    """
    client = AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version="2024-02-01",
    )

    system_prompt = """
    You are Copilot, the generative AI brain of the ACS-WPP Interplanetary AI Mesh.
    Your role is to analyse incoming WhatsApp messages and generate a Modulation
    Instruction Set (MIS) as a JSON object with the following fields:
    - strategy: the communication strategy (e.g. "answer_query", "proactive_upsell", "escalate_human")
    - response_text: the exact message text to send back to the user
    - ai_tone: the tone of the response (e.g. "professional", "empathetic", "enthusiastic")
    - escalate: boolean — whether to escalate to a human agent
    - record_intent: boolean — always true for blockchain anchoring
    Return ONLY valid JSON, no markdown, no explanation.
    """

    history_context = "\n".join(
        [f"[{h['timestamp']}] User: {h['message']}" for h in history]
    ) or "No previous interactions."

    user_prompt = f"""
    User number: {user_number}
    Conversation history from blockchain:
    {history_context}

    New incoming message: "{user_message}"

    Generate the MIS JSON now.
    """

    response = client.chat.completions.create(
        model=AZURE_OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
    )

    mis = json.loads(response.choices[0].message.content)
    print(f"[Copilot] MIS generated — strategy: {mis.get('strategy')}")
    return mis


# =============================================================================
# STEP 2 — ACS MODULATION ENGINE: Translate MIS into WhatsApp action
# =============================================================================

def acs_modulate_and_send(mis: dict, recipient_number: str) -> str:
    """
    The ACS Modulation Engine receives the MIS from Copilot and executes
    the appropriate action via Azure Communication Services → Meta WPP.

    Args:
        mis:              The Modulation Instruction Set from Copilot.
        recipient_number: The WhatsApp number to deliver the message to.

    Returns:
        The ACS message ID for tracking.
    """
    acs_client = NotificationMessagesClient.from_connection_string(ACS_CONNECTION_STRING)

    if mis.get("escalate"):
        # Escalation: notify the human agent channel instead
        print("[ACS] Escalating to human agent.")
        return "escalated"

    # Build and send a text message via Meta WPP
    message_content = TextNotificationContent(
        channel_registration_id=WPP_CHANNEL_ID,
        to=[recipient_number],
        content=mis["response_text"],
    )

    response = acs_client.send(message_content)
    message_id = response.receipts[0].message_id if response.receipts else "unknown"

    print(f"[ACS] Message delivered via Meta WPP. Message ID: {message_id}")
    return message_id


# =============================================================================
# STEP 3 — AZURE BLOCKCHAIN: Anchor the full interaction
# =============================================================================

def blockchain_anchor_interaction(
    sender: str,
    original_message: str,
    mis: dict,
    acs_message_id: str,
) -> str:
    """
    Anchors the complete interaction — user message, Copilot MIS, and ACS
    delivery receipt — to the Azure Blockchain as an immutable record.

    Args:
        sender:           The WhatsApp number of the user.
        original_message: The raw message text from the user.
        mis:              The Modulation Instruction Set generated by Copilot.
        acs_message_id:   The ACS delivery receipt ID.

    Returns:
        The blockchain transaction hash.
    """
    w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_NODE_URL))
    ledger = w3.eth.contract(address=LEDGER_CONTRACT_ADDR, abi=LEDGER_CONTRACT_ABI)

    # Hash the original message content — raw text is never stored on-chain
    message_hash = w3.to_bytes(hexstr=hashlib.sha256(original_message.encode()).hexdigest())

    tx_hash = ledger.functions.anchorMessage(
        sender,                          # _sender
        "business",                      # _recipient (the business account)
        message_hash,                    # _messageHash
        "earth",                         # _planet
    ).transact({"from": w3.eth.accounts[0]})

    print(f"[Blockchain] Interaction anchored. TX: {tx_hash.hex()}")
    return tx_hash.hex()


# =============================================================================
# MAIN PIPELINE — Orchestrates the full Copilot → ACS → WPP → Blockchain loop
# =============================================================================

def run_pipeline(incoming_webhook_payload: dict):
    """
    Orchestrates the full generative communication pipeline triggered by an
    incoming WhatsApp message from the Meta WPP webhook.

    Args:
        incoming_webhook_payload: The raw JSON payload from the Meta WPP webhook.
    """
    # Extract message data from the WPP webhook payload
    entry   = incoming_webhook_payload["entry"][0]
    change  = entry["changes"][0]["value"]
    message = change["messages"][0]

    user_number  = message["from"]
    user_text    = message["text"]["body"]

    print(f"\n{'='*60}")
    print(f"[Pipeline] Incoming message from {user_number}: '{user_text}'")
    print(f"{'='*60}")

    # Step 1 — Copilot generates the Modulation Instruction Set
    # In production, `history` is queried from the blockchain ledger
    history = []
    mis = copilot_generate_mis(user_text, user_number, history)

    # Step 2 — ACS Modulation Engine delivers the response via Meta WPP
    acs_message_id = acs_modulate_and_send(mis, user_number)

    # Step 3 — Azure Blockchain anchors the full interaction
    tx_hash = blockchain_anchor_interaction(
        sender=user_number,
        original_message=user_text,
        mis=mis,
        acs_message_id=acs_message_id,
    )

    print(f"\n[Pipeline] ✅ Full loop complete.")
    print(f"  Strategy  : {mis.get('strategy')}")
    print(f"  ACS Msg ID: {acs_message_id}")
    print(f"  Blockchain: {tx_hash}")
    print(f"{'='*60}\n")


# =============================================================================
# ENTRY POINT — Simulates a Meta WPP webhook payload for local testing
# =============================================================================

if __name__ == "__main__":
    sample_webhook_payload = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "+15550001234",
                        "type": "text",
                        "text": {"body": "Hello, I need help with my interplanetary shipment."}
                    }]
                }
            }]
        }]
    }

    run_pipeline(sample_webhook_payload)
