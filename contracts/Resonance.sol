// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.8/interfaces/VRFCoordinatorV2Interface.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBaseV2.sol";


contract Resonance is ERC1155, Ownable, VRFConsumerBaseV2 {
    uint256 public item_counter;

    VRFCoordinatorV2Interface COORDINATOR;

    // Your subscription ID.
    uint64 s_subscriptionId;

    // Rinkeby coordinator. For other networks,
    // see https://docs.chain.link/docs/vrf-contracts/#configurations
    address vrfCoordinator = 0x6168499c0cFfCaCD319c818142124B7A15E857ab;

    // The gas lane to use, which specifies the maximum gas price to bump to.
    // For a list of available gas lanes on each network,
    // see https://docs.chain.link/docs/vrf-contracts/#configurations
    bytes32 keyHash = 0xd89b2bf150e3b9e13446986e571fb9cab24b13cea0a43ea20a6049a85cc807cc;

    // Depends on the number of requested values that you want sent to the
    // fulfillRandomWords() function. Storing each word costs about 20,000 gas,
    // so 100,000 is a safe default for this example contract. Test and adjust
    // this limit based on the network that you select, the size of the request,
    // and the processing of the callback request in the fulfillRandomWords()
    // function.
    uint32 callbackGasLimit = 100000;

    // The default is 3, but you can set this higher.
    uint16 requestConfirmations = 3;

    uint32 numWords =  2;
    uint256 public s_requestId;
    address s_owner;

    enum Scarcity{COMMON, RARE, ULTRA_RARE}
    mapping(uint256 => Scarcity) public tokenIdToScarcity;
    mapping(uint256 => address) public requestIdToSender;
    event requestedCollectible(uint256 indexed requestId, address requester);
    event scarcityAssigned(uint256 indexed tokenId, Scarcity scarcity);

    constructor(uint64 subscriptionId) ERC1155("ipfs://QmPNJWNFpw3JyMjPEjN7XzJ2ivxo4SuZ24u2f9Kav3rdHj/{id}.json") VRFConsumerBaseV2(vrfCoordinator){
        item_counter = 0;

        COORDINATOR = VRFCoordinatorV2Interface(vrfCoordinator);
        s_owner = msg.sender;
        s_subscriptionId = subscriptionId;
    }

    function mint(uint256 amount) public onlyOwner returns(uint256) {
        s_requestId = COORDINATOR.requestRandomWords(
            keyHash,
            s_subscriptionId,
            requestConfirmations,
            callbackGasLimit,
            numWords
        );
        requestIdToSender[s_requestId] = msg.sender;
        emit requestedCollectible(s_requestId, msg.sender);
    }

    function randomToScarcity(uint256 randomNum) public returns(int8) {
        // TODO: make function view?
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

    function fulfillRandomWords(
        uint256 requestId, /* requestId */
        uint256[] memory randomWords
    ) internal override {
        uint32 randomNum = randomWords[0] % 1000;
        Scarcity scarcity = randomToScarcity(randomNum);
        
        uint256 newTokenId = item_counter;
        tokenIdToScarcity[newTokenId] = scarcity; // Can change this stuff from tokenId
        emit scarcityAssigned(newTokenId, scarcity);
        address owner = requestIdToSender[requestId];
        _mint(owner, item_counter, 1, ""); // TODO: somehow pass token amount to this
        item_counter += 1;
    }
}