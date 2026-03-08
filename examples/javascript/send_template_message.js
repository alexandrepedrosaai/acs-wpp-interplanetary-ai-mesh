/**
 * Example: Sending a Template Message via Azure Communication Services
 * This example demonstrates how to send a WhatsApp template message using ACS.
 */

const { SmsClient } = require("@azure/communication-sms");

async function sendTemplateMessage() {
    const connectionString = process.env.ACS_CONNECTION_STRING || "<connection-string>";
    const smsClient = new SmsClient(connectionString);

    try {
        await smsClient.send({
            from: process.env.WHATSAPP_NUMBER || "<whatsapp-number>",
            to: process.env.USER_NUMBER || "<user-number>",
            message: "Hello from ACS WhatsApp Integration!"
        });
        
        console.log("Template message sent successfully!");
    } catch (error) {
        console.error("Error sending message:", error);
    }
}

sendTemplateMessage();
