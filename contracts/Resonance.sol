// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@chainlink/contracts/src/v0.8/interfaces/LinkTokenInterface.sol";
import "@chainlink/contracts/src/v0.8/interfaces/VRFCoordinatorV2Interface.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBaseV2.sol";


contract Resonance is ERC1155, VRFConsumerBaseV2 {
    uint256 public item_counter;

    LinkTokenInterface LINKTOKEN;
    VRFCoordinatorV2Interface COORDINATOR;

    uint64 public s_subscriptionId;

    // Rinkeby coordinator
    address vrfCoordinator = 0x6168499c0cFfCaCD319c818142124B7A15E857ab;

    // Rinkeby LINK token contract
    address link_token_contract = 0x01BE23585060835E02B77ef475b0Cc51aA1e0709;

    // The gas lane to use, which specifies the maximum gas price to bump to
    bytes32 keyHash = 0xd89b2bf150e3b9e13446986e571fb9cab24b13cea0a43ea20a6049a85cc807cc;

    // Depends on the number of requested values that you want sent to the
    // fulfillRandomWords() function. Storing each word costs about 20,000 gas,
    // so 100,000 is a safe default for this example contract. Test and adjust
    // this limit based on the network that you select, the size of the request,
    // and the processing of the callback request in the fulfillRandomWords()
    // function.
    uint32 callbackGasLimit = 100000;

    // Number of confirmations the Chainlink node should wait before responding
    uint16 requestConfirmations = 3;

    uint32 numWords =  2;
    uint256 public s_requestId;
    uint256[] public randomNums;
    address s_owner;

    enum Scarcity{COMMON, RARE, ULTRA_RARE}
    mapping(uint256 => Scarcity) public itemIdToScarcity;
    mapping(uint256 => address) public requestIdToSender;
    event requestedCollectible(uint256 indexed requestId, address requester);
    event randomWordsGenerated(uint256[] randomNumbers);
    event scarcityAssigned(uint256 indexed itemId, Scarcity scarcity);

    constructor() ERC1155("ipfs://QmPNJWNFpw3JyMjPEjN7XzJ2ivxo4SuZ24u2f9Kav3rdHj/{id}.json") VRFConsumerBaseV2(vrfCoordinator){
        // TODO: change IPFS root
        item_counter = 0;

        COORDINATOR = VRFCoordinatorV2Interface(vrfCoordinator);
        LINKTOKEN = LinkTokenInterface(link_token_contract);
        s_owner = msg.sender;
        createNewSubscription();
        
        // Mint 1000 of Artist's currency
        _mint(address(this), 0, 1000, "");
        item_counter += 1;
    }

    /* Fund subscription and request random words */
    function generateRandomWords() public {
        
        // 400000000000000000 = 0.4 LINK
        LINKTOKEN.transferAndCall(address(COORDINATOR), 2000000000000000000, abi.encode(s_subscriptionId)); 
        
        s_requestId = COORDINATOR.requestRandomWords(
            keyHash,
            s_subscriptionId,
            requestConfirmations,
            callbackGasLimit,
            numWords
        );
        requestIdToSender[s_requestId] = msg.sender; // Create mapping from owner to random words for minting
        emit requestedCollectible(s_requestId, msg.sender);
    }

    function fulfillRandomWords(
        uint256 requestId, /* requestId */
        uint256[] memory randomWords
    ) internal override {
        randomNums = randomWords;
        //TODO emit event when successful
        emit randomWordsGenerated(randomNums);
    }

    /* Map random number to distribution of scarcity */
    function randomToScarcity(uint256 randomNum) private pure returns(Scarcity) {
        if (randomNum < 1){
            return Scarcity(2);
        }
        else if (randomNum < 100){
            return Scarcity(1);
        }
        else{
            return Scarcity(0);
        }
    }

    /* Calculate scarcity of non-fungible artwork */
    function mint_nf_artwork(address owner) public {
        // uint256 randomScarcity = randomNums[0] % 1000; // TODO: Uncomment for actual scarcity distribution
        // Scarcity scarcity = randomToScarcity(randomScarcity);
        Scarcity scarcity = Scarcity(randomNums[0] % 3);
        itemIdToScarcity[item_counter] = scarcity;
        emit scarcityAssigned(item_counter, scarcity);
        _mint(owner, item_counter, 1, "");
        item_counter += 1;
    }
    
    /* Calculate if minter should be dropped 1 currency of artist */
    function transfer_currency(address owner) public {
        // TODO: create mapping of owners to tokens
        uint256 randomDrop = randomNums[1] % 2;  // 50% chance
        if (randomDrop <= 1) {
            safeTransferFrom(address(this), owner, 0, 1, "0x0"); // Artist currency has ID = 0
        }
    }

    // Create a new subscription when the contract is initially deployed.
    function createNewSubscription() private onlyOwner {
        s_subscriptionId = COORDINATOR.createSubscription();
        // Add this contract as a consumer of its own subscription.
        COORDINATOR.addConsumer(s_subscriptionId, address(this));
    }

    // Assumes this contract owns link.
    // 1000000000000000000 = 1 LINK
    function topUpSubscription(uint256 amount) external onlyOwner {
        LINKTOKEN.transferAndCall(address(COORDINATOR), amount, abi.encode(s_subscriptionId));
    }

    function cancelSubscription(address receivingWallet) external onlyOwner {
        // Cancel the subscription and send the remaining LINK to a wallet address.
        COORDINATOR.cancelSubscription(s_subscriptionId, receivingWallet);
        s_subscriptionId = 0;
    }

    function withdraw(uint256 amount, address to) external onlyOwner {
        // Transfer the remaining LINK on this contract to a wallet address
        LINKTOKEN.transfer(to, amount);
    }

    modifier onlyOwner() {
        require(msg.sender == s_owner);
        _;
    }
}