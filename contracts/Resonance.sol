// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@chainlink/contracts/src/v0.8/interfaces/LinkTokenInterface.sol";
import "@chainlink/contracts/src/v0.8/interfaces/VRFCoordinatorV2Interface.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBaseV2.sol";
import "./Queue.sol";


contract Resonance is ERC1155, VRFConsumerBaseV2 {
    using Queue for Queue.Uint256Queue;

    uint256 public item_counter;

    LinkTokenInterface LINKTOKEN;
    VRFCoordinatorV2Interface COORDINATOR;
    
    Queue.Uint256Queue delta_queue;
    uint256 public delta_sum = 0;
    uint256 public prev_block = 0;
    uint256 MAX_QUEUE_SIZE = 50;

    uint64 public s_subscriptionId;

    // Rinkeby coordinator
    address vrfCoordinator = 0x2Ca8E0C643bDe4C2E08ab1fA0da3401AdAD7734D;

    // Rinkeby LINK token contract
    address link_token_contract = 0x326C977E6efc84E512bB9C30f76E30c160eD06FB;

    // The gas lane to use, which specifies the maximum gas price to bump to
    bytes32 keyHash = 0x79d3d8832d904592c0bf9818b621522c988bb8b0c05cdc3b15aea1b6e8db0c15;

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
    mapping(uint256 => uint256) public itemIdToPopularity;
    event requestedCollectible(uint256 indexed requestId, address requester);
    event randomWordsGenerated(uint256[] randomNumbers);
    event scarcityAssigned(uint256 indexed itemId, Scarcity scarcity);
    event defundContract(uint256 balance);
    event popularityAssigned(uint256 indexed itemId, uint256 popularity);

    constructor(address vrfCoordinator, address link_token_contract, bytes32 keyHash) ERC1155("ipfs://QmPNJWNFpw3JyMjPEjN7XzJ2ivxo4SuZ24u2f9Kav3rdHj/{id}.json") VRFConsumerBaseV2(vrfCoordinator){
        item_counter = 0;

        COORDINATOR = VRFCoordinatorV2Interface(vrfCoordinator);
        LINKTOKEN = LinkTokenInterface(link_token_contract);
        delta_queue.initialize();
        s_owner = msg.sender;
        createNewSubscription();
        
        // Mint 1000 of Artist's currency
        _mint(address(this), 0, 1000, "");
        item_counter += 1;
    }

    /* Fund subscription and request random words */
    function generateRandomWords() public {        
        s_requestId = COORDINATOR.requestRandomWords(
            keyHash,
            s_subscriptionId,
            requestConfirmations,
            callbackGasLimit,
            numWords
        );
    }

    function fulfillRandomWords(
        uint256 requestId, /* requestId */
        uint256[] memory randomWords
    ) internal override {
        randomNums = randomWords;
        emit randomWordsGenerated(randomNums);
    }

    /* Map random number to distribution of scarcity */
    function randomToScarcity(uint256 randomNum) private pure returns(Scarcity) {
        if (randomNum < 1){
            return Scarcity(2);
        }
        else if (randomNum < 50){
            return Scarcity(1);
        }
        else{
            return Scarcity(0);
        }
    }

    /* Calculate scarcity of non-fungible artwork */
    function mint_nf_artwork() public {
        if (delta_queue.length() >= MAX_QUEUE_SIZE){
            delta_sum -= delta_queue.dequeue();
        }
        if (prev_block > 0) {
            delta_queue.enqueue(block.number - prev_block);
            delta_sum += block.number - prev_block;
        }
        prev_block = block.number;

        uint256 popularity = getPopularity();
        itemIdToPopularity[item_counter] = popularity;
        emit popularityAssigned(item_counter, popularity);
        // Scarcity scarcity = randomToScarcity(randomNums[0] % 500); // TODO: Uncomment for actual scarcity distribution
        Scarcity scarcity = Scarcity(randomNums[0] % 3);
        itemIdToScarcity[item_counter] = scarcity;
        emit scarcityAssigned(item_counter, scarcity);
        _mint(msg.sender, item_counter, 1, abi.encodePacked(popularity));
        item_counter += 1;

        transfer_currency();
        
    }

    function getPopularity() public view returns(uint256) {
        if (delta_queue.length() <= 1){
            return 0;
        }
        uint256 avg_delta = delta_sum / delta_queue.length();
        return (15000000 / avg_delta) + (item_counter * 1000000 / avg_delta);
    }
    
    /* Calculate if minter should be dropped 1 currency of artist */
    function transfer_currency() private {
        uint256 randomDrop = randomNums[1] % 2;  // 50% chance
        if (randomDrop < 1) {
            _safeTransferFrom(address(this), msg.sender, 0, 1, "0x0"); // Artist currency has ID = 0
        }
    }

    /* The following queue functions are used for debugging purposes */
    function peekFirst() public view returns(uint256) {
        return delta_queue.peek();
    }

    function peekLast() public view returns(uint256) {
        return delta_queue.peekLast();
    }

    function queueLen() public view returns(uint256) {
        return delta_queue.length();
    }

    function setURI(string memory uri) external onlyOwner {
        _setURI(uri);
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
        emit defundContract(LINKTOKEN.balanceOf(address(this))); // Emit contract's balance of LINK
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