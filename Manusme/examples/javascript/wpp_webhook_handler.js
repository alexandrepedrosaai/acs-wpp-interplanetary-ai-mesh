/**
 * Manusme — Azure Function: Meta WPP Webhook Handler
 * Author: Alexandre Pedrosa — EVP Multimodal AI Engineer at Meta and Microsoft Azure
 * © 2025-2026 Alexandre Pedrosa. All Rights Reserved.
 *
 * This Azure Function serves as the entry point for all Meta WhatsApp Business
 * Platform (WPP) webhook events. It handles:
 *   - Webhook verification (GET)
 *   - Incoming message processing → triggers the Copilot → ACS → Blockchain pipeline (POST)
 */

const { app } = require("@azure/functions");
const { OpenAIClient, AzureKeyCredential } = require("@azure/openai");
const { NotificationMessagesClient } = require("@azure/communication-messages");

// =============================================================================
// WEBHOOK VERIFICATION — Meta WPP requires a GET verification handshake
// =============================================================================

app.http("wppWebhookVerify", {
    methods: ["GET"],
    authLevel: "anonymous",
    route: "webhook/whatsapp",
    handler: async (request, context) => {
        const VERIFY_TOKEN = process.env.WPP_VERIFY_TOKEN;

        const mode      = request.query.get("hub.mode");
        const token     = request.query.get("hub.verify_token");
        const challenge = request.query.get("hub.challenge");

        if (mode === "subscribe" && token === VERIFY_TOKEN) {
            context.log("[Webhook] Meta WPP verification successful.");
            return { status: 200, body: challenge };
        }

        context.log("[Webhook] Meta WPP verification failed.");
        return { status: 403, body: "Forbidden" };
    },
});

// =============================================================================
// INCOMING MESSAGE HANDLER — Processes all incoming WPP events
// =============================================================================

app.http("wppWebhookReceive", {
    methods: ["POST"],
    authLevel: "anonymous",
    route: "webhook/whatsapp",
    handler: async (request, context) => {
        const payload = await request.json();

        // Extract message from WPP payload structure
        const entry   = payload?.entry?.[0];
        const change  = entry?.changes?.[0]?.value;
        const message = change?.messages?.[0];

        if (!message || message.type !== "text") {
            context.log("[Webhook] Non-text message received — skipping pipeline.");
            return { status: 200, body: "OK" };
        }

        const userNumber = message.from;
        const userText   = message.text.body;

        context.log(`[Webhook] Message from ${userNumber}: "${userText}"`);

        try {
            // Step 1 — Copilot generates the Modulation Instruction Set
            const mis = await generateMIS(userText, userNumber, context);

            // Step 2 — ACS sends the response via Meta WPP
            const acsMessageId = await sendViaACS(mis, userNumber, context);

            // Step 3 — Log to blockchain (async, non-blocking)
            anchorToBlockchain(userNumber, userText, mis, acsMessageId, context).catch(
                (err) => context.log(`[Blockchain] Anchor failed: ${err.message}`)
            );

            return { status: 200, body: "OK" };
        } catch (err) {
            context.log(`[Pipeline] Error: ${err.message}`);
            return { status: 500, body: "Internal Server Error" };
        }
    },
});

// =============================================================================
// STEP 1 — COPILOT: Generate Modulation Instruction Set via Azure OpenAI
// =============================================================================

async function generateMIS(userText, userNumber, context) {
    const openaiClient = new OpenAIClient(
        process.env.AZURE_OPENAI_ENDPOINT,
        new AzureKeyCredential(process.env.AZURE_OPENAI_API_KEY)
    );

    const systemPrompt = `
You are Copilot, the generative AI brain of the ACS-WPP Interplanetary AI Mesh.
Analyse the incoming WhatsApp message and return a JSON Modulation Instruction Set (MIS):
{
  "strategy": "answer_query | proactive_upsell | escalate_human",
  "response_text": "<exact message to send>",
  "ai_tone": "professional | empathetic | enthusiastic",
  "escalate": false
}
Return ONLY valid JSON.`;

    const response = await openaiClient.getChatCompletions(
        process.env.AZURE_OPENAI_DEPLOYMENT || "gpt-4o",
        [
            { role: "system", content: systemPrompt },
            { role: "user",   content: `User: ${userNumber}\nMessage: "${userText}"` },
        ],
        { responseFormat: { type: "json_object" }, temperature: 0.7 }
    );

    const mis = JSON.parse(response.choices[0].message.content);
    context.log(`[Copilot] MIS generated — strategy: ${mis.strategy}`);
    return mis;
}

// =============================================================================
// STEP 2 — ACS MODULATION ENGINE: Deliver response via Meta WPP
// =============================================================================

async function sendViaACS(mis, recipientNumber, context) {
    if (mis.escalate) {
        context.log("[ACS] Escalating to human agent.");
        return "escalated";
    }

    const acsClient = NotificationMessagesClient.fromConnectionString(
        process.env.ACS_CONNECTION_STRING
    );

    const result = await acsClient.send({
        channelRegistrationId: process.env.WPP_CHANNEL_ID,
        to: [recipientNumber],
        kind: "text",
        content: mis.response_text,
    });

    const messageId = result.receipts?.[0]?.messageId ?? "unknown";
    context.log(`[ACS] Delivered via Meta WPP. Message ID: ${messageId}`);
    return messageId;
}

// =============================================================================
// STEP 3 — AZURE BLOCKCHAIN: Anchor the interaction (async, fire-and-forget)
// =============================================================================

async function anchorToBlockchain(sender, originalMessage, mis, acsMessageId, context) {
    // In production, this calls the WhatsAppMessageLedger smart contract via web3.js
    // Here we log the intent for demonstration
    const record = {
        sender,
        messageHash: require("crypto")
            .createHash("sha256")
            .update(originalMessage)
            .digest("hex"),
        copilotStrategy: mis.strategy,
        acsMessageId,
        timestamp: new Date().toISOString(),
        planet: "earth",
    };

    context.log(`[Blockchain] Anchoring record: ${JSON.stringify(record)}`);
    // TODO: call ledger.anchorMessage(...) via web3.js
}
