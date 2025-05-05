// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract PriceOracle {
    struct PriceSubmission {
        uint256 price;
        address submitter;
        uint256 timestamp;
        string source;
    }
    
    mapping(string => PriceSubmission[]) public productSubmissions;
    mapping(string => uint256) public verifiedPrices;
    mapping(address => uint256) public submitterReputation;
    
    event PriceSubmitted(
        string indexed productId,
        uint256 price,
        address submitter,
        uint256 timestamp
    );
    
    event PriceVerified(
        string indexed productId,
        uint256 price,
        uint256 timestamp
    );
    
    function submitPrice(
        string memory productId,
        uint256 price,
        string memory source
    ) external {
        require(price > 0, "Price must be greater than 0");
        
        productSubmissions[productId].push(PriceSubmission({
            price: price,
            submitter: msg.sender,
            timestamp: block.timestamp,
            source: source
        }));
        
        emit PriceSubmitted(
            productId,
            price,
            msg.sender,
            block.timestamp
        );
    }
    
    function verifyPrice(string memory productId) external {
        PriceSubmission[] storage submissions = productSubmissions[productId];
        require(submissions.length >= 3, "Not enough submissions");
        
        uint256 sum = 0;
        uint256 count = 0;
        
        // Calculate average of most recent submissions within 10% of median
        uint256[] memory prices = new uint256[](submissions.length);
        for (uint i = 0; i < submissions.length; i++) {
            prices[i] = submissions[i].price;
        }
        
        uint256 median = _median(prices);
        uint256 lowerBound = median * 90 / 100;
        uint256 upperBound = median * 110 / 100;
        
        for (uint i = 0; i < submissions.length; i++) {
            if (submissions[i].price >= lowerBound && 
                submissions[i].price <= upperBound) {
                sum += submissions[i].price;
                count++;
                submitterReputation[submissions[i].submitter] += 1;
            }
        }
        
        uint256 verifiedPrice = sum / count;
        verifiedPrices[productId] = verifiedPrice;
        
        emit PriceVerified(
            productId,
            verifiedPrice,
            block.timestamp
        );
    }
    
    function _median(uint256[] memory array) private pure returns (uint256) {
        require(array.length > 0, "Array cannot be empty");
        
        uint256[] memory sorted = _sort(array);
        uint256 middle = sorted.length / 2;
        
        if (sorted.length % 2 == 0) {
            return (sorted[middle - 1] + sorted[middle]) / 2;
        } else {
            return sorted[middle];
        }
    }
    
    function _sort(uint256[] memory array) private pure returns (uint256[] memory) {
        uint256[] memory sorted = new uint256[](array.length);
        
        for (uint i = 0; i < array.length; i++) {
            sorted[i] = array[i];
        }
        
        for (uint i = 0; i < sorted.length; i++) {
            for (uint j = i + 1; j < sorted.length; j++) {
                if (sorted[i] > sorted[j]) {
                    (sorted[i], sorted[j]) = (sorted[j], sorted[i]);
                }
            }
        }
        
        return sorted;
    }
    
    function getVerifiedPrice(string memory productId) external view returns (uint256) {
        return verifiedPrices[productId];
    }
    
    function getSubmitterReputation(address submitter) external view returns (uint256) {
        return submitterReputation[submitter];
    }
}
