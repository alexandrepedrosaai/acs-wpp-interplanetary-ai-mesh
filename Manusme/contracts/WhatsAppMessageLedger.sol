// SPDX-License-Identifier: All Rights Reserved
// © 2025-2026 Alexandre Pedrosa. All Rights Reserved.
// EVP Multimodal AI Engineer at Meta and Microsoft Azure

pragma solidity ^0.8.20;

/**
 * @title WhatsAppMessageLedger
 * @author Alexandre Pedrosa
 * @notice This contract anchors Meta WhatsApp Business Platform messages
 *         to the Azure Blockchain, providing an immutable audit trail.
 *         It is the core component of the Manusme Azure Blockchain integration.
 */
contract WhatsAppMessageLedger {

    // =========================================================================
    // EVENTS
    // =========================================================================

    /// @notice Emitted when a new WhatsApp message is anchored to the blockchain.
    event MessageAnchored(
        bytes32 indexed messageId,
        string indexed sender,
        bytes32 messageHash,
        uint256 timestamp,
        string status
    );

    /// @notice Emitted when the AI validation result is recorded for a message.
    event AIValidationRecorded(
        bytes32 indexed messageId,
        uint8 validationScore,
        bool isThreat,
        string aiModel
    );

    /// @notice Emitted when a message delivery is confirmed.
    event DeliveryConfirmed(
        bytes32 indexed messageId,
        string recipient,
        uint256 deliveryTimestamp
    );

    // =========================================================================
    // DATA STRUCTURES
    // =========================================================================

    /// @notice Represents a single WhatsApp message record on the blockchain.
    struct MessageRecord {
        bytes32 messageId;       // Unique identifier for the message
        string sender;           // WhatsApp number of the sender
        string recipient;        // WhatsApp number of the recipient
        bytes32 messageHash;     // SHA-256 hash of the message content
        uint256 timestamp;       // Block timestamp when anchored
        string status;           // e.g., "anchored", "validated", "delivered"
        uint8 aiValidationScore; // AI confidence score (0-100)
        bool isThreat;           // AI threat detection flag
        bool isDelivered;        // Delivery confirmation flag
        string planet;           // Origin planet: "earth", "moon", "mars"
    }

    // =========================================================================
    // STATE VARIABLES
    // =========================================================================

    /// @notice The owner of the contract (ACS Gateway).
    address public owner;

    /// @notice The authorized AI Oracle address.
    address public aiOracle;

    /// @notice Mapping from message ID to its record.
    mapping(bytes32 => MessageRecord) public messageRecords;

    /// @notice Total number of messages anchored.
    uint256 public totalMessages;

    // =========================================================================
    // MODIFIERS
    // =========================================================================

    modifier onlyOwner() {
        require(msg.sender == owner, "Caller is not the owner");
        _;
    }

    modifier onlyAIOracle() {
        require(msg.sender == aiOracle, "Caller is not the AI Oracle");
        _;
    }

    // =========================================================================
    // CONSTRUCTOR
    // =========================================================================

    constructor(address _aiOracle) {
        owner = msg.sender;
        aiOracle = _aiOracle;
    }

    // =========================================================================
    // CORE FUNCTIONS
    // =========================================================================

    /**
     * @notice Anchors a new WhatsApp message to the blockchain.
     * @dev Called by the ACS Gateway upon receiving a message from the WPP webhook.
     * @param _sender The WhatsApp number of the sender.
     * @param _recipient The WhatsApp number of the recipient.
     * @param _messageHash The SHA-256 hash of the message content.
     * @param _planet The origin planet of the message.
     * @return messageId The unique ID assigned to this message on the blockchain.
     */
    function anchorMessage(
        string calldata _sender,
        string calldata _recipient,
        bytes32 _messageHash,
        string calldata _planet
    ) external onlyOwner returns (bytes32 messageId) {
        // Generate a unique message ID
        messageId = keccak256(
            abi.encodePacked(_sender, _recipient, _messageHash, block.timestamp, totalMessages)
        );

        // Store the message record
        messageRecords[messageId] = MessageRecord({
            messageId: messageId,
            sender: _sender,
            recipient: _recipient,
            messageHash: _messageHash,
            timestamp: block.timestamp,
            status: "anchored",
            aiValidationScore: 0,
            isThreat: false,
            isDelivered: false,
            planet: _planet
        });

        totalMessages++;

        emit MessageAnchored(messageId, _sender, _messageHash, block.timestamp, "anchored");

        return messageId;
    }

    /**
     * @notice Records the AI validation result for a message.
     * @dev Called by the authorized AI Oracle after processing the message.
     * @param _messageId The ID of the message to update.
     * @param _score The AI validation score (0-100).
     * @param _isThreat Whether the AI flagged the message as a threat.
     * @param _aiModel The name of the AI model used for validation.
     */
    function recordAIValidation(
        bytes32 _messageId,
        uint8 _score,
        bool _isThreat,
        string calldata _aiModel
    ) external onlyAIOracle {
        MessageRecord storage record = messageRecords[_messageId];
        require(record.timestamp != 0, "Message not found");

        record.aiValidationScore = _score;
        record.isThreat = _isThreat;
        record.status = _isThreat ? "threat_detected" : "validated";

        emit AIValidationRecorded(_messageId, _score, _isThreat, _aiModel);
    }

    /**
     * @notice Confirms the delivery of a message.
     * @dev Called by the ACS Gateway upon receiving a delivery receipt from WPP.
     * @param _messageId The ID of the message that was delivered.
     */
    function confirmDelivery(bytes32 _messageId) external onlyOwner {
        MessageRecord storage record = messageRecords[_messageId];
        require(record.timestamp != 0, "Message not found");
        require(!record.isDelivered, "Delivery already confirmed");

        record.isDelivered = true;
        record.status = "delivered";

        emit DeliveryConfirmed(_messageId, record.recipient, block.timestamp);
    }

    // =========================================================================
    // VIEW FUNCTIONS
    // =========================================================================

    /**
     * @notice Retrieves the full record of a message.
     * @param _messageId The ID of the message.
     * @return The MessageRecord struct.
     */
    function getMessage(bytes32 _messageId) external view returns (MessageRecord memory) {
        require(messageRecords[_messageId].timestamp != 0, "Message not found");
        return messageRecords[_messageId];
    }

    /**
     * @notice Updates the AI Oracle address.
     * @param _newOracle The address of the new AI Oracle.
     */
    function setAIOracle(address _newOracle) external onlyOwner {
        aiOracle = _newOracle;
    }
}
