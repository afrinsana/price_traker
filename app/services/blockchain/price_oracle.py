from web3 import Web3
from web3.middleware import geth_poa_middleware
from typing import Dict, Optional
import json
import os
from datetime import datetime
from app.core.config import settings
from app.core.logging import logger
from app.utils.exceptions import BlockchainError

class PriceOracle:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.BLOCKCHAIN_RPC_URL))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Load contract ABI
        with open('app/services/blockchain/contracts/PriceOracle.json') as f:
            self.contract_abi = json.load(f)
            
        self.contract = self.w3.eth.contract(
            address=settings.PRICE_ORACLE_CONTRACT_ADDRESS,
            abi=self.contract_abi
        )
        
    def submit_price(self, product_id: str, price: float, metadata: Dict) -> str:
        """Submit price data to blockchain"""
        try:
            # Prepare transaction
            tx_data = {
                'productId': product_id,
                'price': int(price * 100),  # Store as integer to avoid float precision
                'source': metadata.get('source', ''),
                'timestamp': metadata.get('timestamp', int(datetime.now().timestamp())),
                'submitter': metadata.get('submitter', '')
            }
            
            # Build and send transaction
            tx = self.contract.functions.submitPrice(
                tx_data['productId'],
                tx_data['price'],
                tx_data['source'],
                tx_data['timestamp'],
                tx_data['submitter']
            ).buildTransaction({
                'chainId': settings.BLOCKCHAIN_CHAIN_ID,
                'gas': 200000,
                'gasPrice': self.w3.toWei('50', 'gwei'),
                'nonce': self.w3.eth.getTransactionCount(settings.BLOCKCHAIN_WALLET_ADDRESS),
            })
            
            # Sign and send
            signed_tx = self.w3.eth.account.signTransaction(
                tx, private_key=settings.BLOCKCHAIN_PRIVATE_KEY)
            tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
            
            return tx_hash.hex()
            
        except Exception as e:
            logger.error(f"Blockchain submission failed: {str(e)}")
            raise BlockchainError(f"Failed to submit price: {str(e)}")

    def get_verified_price(self, product_id: str) -> Optional[Dict]:
        """Get verified price from blockchain"""
        try:
            result = self.contract.functions.getVerifiedPrice(product_id).call()
            return {
                'price': result[0] / 100,
                'timestamp': result[1],
                'source': result[2],
                'confidence': result[3] / 100
            }
        except Exception as e:
            logger.error(f"Failed to get verified price: {str(e)}")
            return None

    # ... (other blockchain interaction methods)