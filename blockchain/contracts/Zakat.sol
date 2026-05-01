// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ZakatGovernance {

    address public owner;

    struct Donation {
        address donor;
        uint amount;
    }

    struct Request {
        uint id;
        string purpose;
        uint amount;
        address payable recipient;
        uint approvals;
        bool completed;
        mapping(address => bool) approvedBy;
    }

    Donation[] public donations;
    Request[] public requests;

    mapping(address => bool) public donors;
    mapping(address => bool) public authorities;

    uint public totalFunds;

    constructor() {
        owner = msg.sender;
    }

    // --- DONATION ---
    function donate() public payable {
        require(msg.value > 0, "Send ETH");

        donations.push(Donation(msg.sender, msg.value));
        donors[msg.sender] = true;
        totalFunds += msg.value;
    }

    // --- ADD AUTHORITY ---
    function addAuthority(address _auth) public {
        require(msg.sender == owner, "Only owner");
        authorities[_auth] = true;
    }

    // --- CREATE REQUEST ---
    function createRequest(string memory _purpose, uint _amount, address payable _recipient) public {
        require(msg.sender == owner, "Only org");

        Request storage r = requests.push();
        r.id = requests.length - 1;
        r.purpose = _purpose;
        r.amount = _amount;
        r.recipient = _recipient;
        r.completed = false;
        r.approvals = 0;
    }

    // --- APPROVE REQUEST ---
    function approveRequest(uint _id) public {
        Request storage r = requests[_id];

        require(donors[msg.sender] || authorities[msg.sender], "Not allowed");
        require(!r.approvedBy[msg.sender], "Already approved");

        r.approvedBy[msg.sender] = true;
        r.approvals++;
    }

    // --- EXECUTE REQUEST ---
    function executeRequest(uint _id) public {
        Request storage r = requests[_id];

        require(!r.completed, "Already done");
        require(r.approvals >= 2, "Not enough approvals"); // adjustable rule
        require(address(this).balance >= r.amount, "Insufficient funds");

        r.recipient.transfer(r.amount);
        r.completed = true;
    }

    function getBalance() public view returns(uint) {
        return address(this).balance;
    }
}