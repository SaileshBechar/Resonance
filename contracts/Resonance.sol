// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract Resonance is ERC1155, Ownable {
    uint256 public item_counter;

    // https://gateway.pinata.cloud/ipfs/Qma9iXzp7wfAALg3SLjQreenmZkf2Ki31fvXVmWFZCyCFs/00000000000000000000000000000000000000000000000000000000000001.json
    // "https://raw.githubusercontent.com/akcgjc007/erc1155-Mushroom/main/meta/{id}.json"
    constructor() ERC1155("ipfs://QmPNJWNFpw3JyMjPEjN7XzJ2ivxo4SuZ24u2f9Kav3rdHj/{id}.json") {
        item_counter = 0;
    }

    function mint(uint256 amount) public onlyOwner returns(uint256) {
        _mint(msg.sender, item_counter, amount, "");
    }
}