import hashlib
from web3 import Web3

# This is a conceptual example. In a real-world scenario, you would use a library
# like web3.py to interact with a deployed smart contract.

class BlockchainAnchor:
    def __init__(self, provider_url, contract_address, contract_abi):
        """Initializes the connection to the blockchain.

        Args:
            provider_url (str): The URL of the Azure Blockchain node.
            contract_address (str): The address of the deployed smart contract.
            contract_abi (list): The ABI of the smart contract.
        """
        self.w3 = Web3(Web3.HTTPProvider(provider_url))
        self.contract = self.w3.eth.contract(address=contract_address, abi=contract_abi)

    def anchor_message(self, sender, message_content):
        """Anchors a WhatsApp message to the blockchain.

        Args:
            sender (str): The WhatsApp number of the sender.
            message_content (str): The body of the WhatsApp message.

        Returns:
            str: The transaction hash of the blockchain transaction.
        """
        # Create a hash of the message content for on-chain storage
        message_hash = hashlib.sha256(message_content.encode()).hexdigest()

        # Get the default account to send the transaction from
        # In a real app, this would be managed securely.
        from_account = self.w3.eth.accounts[0]

        # Call the smart contract function to anchor the message
        tx_hash = self.contract.functions.anchorMessage(
            sender,
            message_hash,
            "pending_ai_validation"  # Initial status
        ).transact({"from": from_account})

        return tx_hash.hex()

if __name__ == "__main__":
    # --- Configuration (replace with your actual data) ---
    AZURE_BLOCKCHAIN_NODE_URL = "https://<your-azure-blockchain-node-url>"
    SMART_CONTRACT_ADDRESS = "0x..."
    # The ABI is a large JSON array, usually loaded from a file
    SMART_CONTRACT_ABI = [] 

    # --- Example Usage ---
    # This simulates a payload received from the Meta WPP webhook
    whatsapp_payload = {
        "from": "+1234567890",
        "text": {"body": "Hello, I need assistance with my interplanetary order."}
    }

    try:
        # Initialize the blockchain anchor service
        anchor_service = BlockchainAnchor(
            AZURE_BLOCKCHAIN_NODE_URL,
            SMART_CONTRACT_ADDRESS,
            SMART_CONTRACT_ABI
        )

        # Anchor the incoming WhatsApp message
        transaction_hash = anchor_service.anchor_message(
            sender=whatsapp_payload["from"],
            message_content=whatsapp_payload["text"]["body"]
        )

        print("✅ WhatsApp message successfully anchored to the blockchain.")
        print(f"   Transaction Hash: {transaction_hash}")

    except Exception as e:
        print("❌ Failed to anchor WhatsApp message.")
        print(f"   Error: {e}")
        print("   Please ensure your configuration is correct and the blockchain node is accessible.")
