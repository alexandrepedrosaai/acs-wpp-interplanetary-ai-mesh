/**
 * Example: Sending Interactive Messages (Buttons & Lists)
 * Demonstrates how to send WhatsApp interactive messages with buttons using ACS.
 */

const { WhatsAppClient } = require("@azure/communication-whatsapp");

async function sendInteractiveMessage() {
    const connectionString = process.env.ACS_CONNECTION_STRING || "<connection-string>";
    const client = new WhatsAppClient(connectionString);

    try {
        await client.sendInteractiveMessage({
            from: process.env.BUSINESS_NUMBER || "<business-number>",
            to: process.env.USER_NUMBER || "<user-number>",
            type: "button",
            body: { text: "Choose an option:" },
            action: {
                buttons: [
                    { type: "reply", reply: { id: "opt1", title: "Option 1" } },
                    { type: "reply", reply: { id: "opt2", title: "Option 2" } }
                ]
            }
        });

        console.log("Interactive message sent successfully!");
    } catch (error) {
        console.error("Error sending interactive message:", error);
    }
}

sendInteractiveMessage();
