# The MIT License (MIT)
# Copyright © 2024 Chainswarm Patterns Subnet

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Union, Any

from core.protocol import DetectedPattern, TransactionGraph, GraphEdge
from core.validator.pattern_processing import PatternVerificationResult


class BlockchainNetwork(Enum):
    """Supported blockchain networks"""
    BITCOIN = "bitcoin"
    ETHEREUM = "ethereum"
    BINANCE_SMART_CHAIN = "bsc"
    POLYGON = "polygon"
    AVALANCHE = "avalanche"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    SOLANA = "solana"
    CARDANO = "cardano"
    POLKADOT = "polkadot"
    COSMOS = "cosmos"
    NEAR = "near"
    FANTOM = "fantom"
    CRONOS = "cronos"
    TRON = "tron"
    LITECOIN = "litecoin"
    BITCOIN_CASH = "bitcoin_cash"
    DOGECOIN = "dogecoin"
    MONERO = "monero"
    ZCASH = "zcash"


@dataclass
class Transaction:
    """Standardized transaction representation across blockchains"""
    hash: str
    from_address: str
    to_address: str
    amount: Decimal
    asset_symbol: str
    timestamp: int
    block_number: int
    gas_fee: Decimal
    status: str  # "success", "failed", "pending"
    
    # Blockchain-specific data
    blockchain: BlockchainNetwork
    raw_data: Dict[str, Any]
    
    # Additional metadata
    transaction_type: str  # "transfer", "contract_call", "swap", etc.
    contract_address: Optional[str] = None
    input_data: Optional[str] = None


@dataclass
class BlockInfo:
    """Standardized block information"""
    number: int
    hash: str
    timestamp: int
    transaction_count: int
    blockchain: BlockchainNetwork


@dataclass
class BlockchainConfig:
    """Configuration for blockchain connections"""
    rpc_url: str
    api_key: Optional[str] = None
    rate_limit_per_second: int = 10
    timeout_seconds: int = 30
    retry_attempts: int = 3
    
    # Authentication for private nodes
    rpc_user: Optional[str] = None
    rpc_password: Optional[str] = None
    
    # Additional settings
    use_websocket: bool = False
    websocket_url: Optional[str] = None


class BlockchainInterface(ABC):
    """Abstract interface for blockchain data access"""
    
    @abstractmethod
    async def get_transaction(self, tx_hash: str) -> Optional[Transaction]:
        """Get transaction by hash"""
        pass
    
    @abstractmethod
    async def get_address_transactions(
        self, 
        address: str, 
        start_block: int = None, 
        end_block: int = None,
        limit: int = 1000
    ) -> List[Transaction]:
        """Get transactions for an address"""
        pass
    
    @abstractmethod
    async def verify_address_exists(self, address: str) -> bool:
        """Verify if address exists on blockchain"""
        pass
    
    @abstractmethod
    async def get_block_info(self, block_number: int) -> Optional[BlockInfo]:
        """Get block information"""
        pass
    
    @abstractmethod
    async def get_current_block_number(self) -> int:
        """Get current block number"""
        pass
    
    @abstractmethod
    async def get_address_balance(self, address: str, asset: str = None) -> Decimal:
        """Get address balance for native token or specific asset"""
        pass


class EthereumInterface(BlockchainInterface):
    """Ethereum and EVM-compatible blockchain interface"""
    
    def __init__(self, config: BlockchainConfig):
        self.config = config
        self.blockchain = BlockchainNetwork.ETHEREUM
        # Initialize Web3 connection here
        
    async def get_transaction(self, tx_hash: str) -> Optional[Transaction]:
        """Get Ethereum transaction by hash"""
        try:
            # Implementation would use Web3.py or similar
            # For now, return a placeholder
            return Transaction(
                hash=tx_hash,
                from_address="0x...",
                to_address="0x...",
                amount=Decimal("1.0"),
                asset_symbol="ETH",
                timestamp=1234567890,
                block_number=12345,
                gas_fee=Decimal("0.01"),
                status="success",
                blockchain=self.blockchain,
                raw_data={},
                transaction_type="transfer"
            )
        except Exception as e:
            return None
    
    async def get_address_transactions(
        self, 
        address: str, 
        start_block: int = None, 
        end_block: int = None,
        limit: int = 1000
    ) -> List[Transaction]:
        """Get transactions for Ethereum address"""
        # Implementation using Etherscan API or similar
        return []
    
    async def verify_address_exists(self, address: str) -> bool:
        """Verify if Ethereum address exists"""
        # Check if address has any transaction history or balance
        return True
    
    async def get_block_info(self, block_number: int) -> Optional[BlockInfo]:
        """Get Ethereum block information"""
        return BlockInfo(
            number=block_number,
            hash="0x...",
            timestamp=1234567890,
            transaction_count=100,
            blockchain=self.blockchain
        )
    
    async def get_current_block_number(self) -> int:
        """Get current Ethereum block number"""
        return 18000000
    
    async def get_address_balance(self, address: str, asset: str = None) -> Decimal:
        """Get Ethereum address balance"""
        return Decimal("1.0")


class BitcoinInterface(BlockchainInterface):
    """Bitcoin blockchain interface"""
    
    def __init__(self, config: BlockchainConfig):
        self.config = config
        self.blockchain = BlockchainNetwork.BITCOIN
        # Initialize Bitcoin RPC connection here
    
    async def get_transaction(self, tx_hash: str) -> Optional[Transaction]:
        """Get Bitcoin transaction by hash"""
        try:
            # Implementation would use Bitcoin RPC
            return Transaction(
                hash=tx_hash,
                from_address="bc1...",
                to_address="bc1...",
                amount=Decimal("0.1"),
                asset_symbol="BTC",
                timestamp=1234567890,
                block_number=800000,
                gas_fee=Decimal("0.0001"),
                status="success",
                blockchain=self.blockchain,
                raw_data={},
                transaction_type="transfer"
            )
        except Exception as e:
            return None
    
    async def get_address_transactions(
        self, 
        address: str, 
        start_block: int = None, 
        end_block: int = None,
        limit: int = 1000
    ) -> List[Transaction]:
        """Get transactions for Bitcoin address"""
        return []
    
    async def verify_address_exists(self, address: str) -> bool:
        """Verify if Bitcoin address exists"""
        return True
    
    async def get_block_info(self, block_number: int) -> Optional[BlockInfo]:
        """Get Bitcoin block information"""
        return BlockInfo(
            number=block_number,
            hash="000000...",
            timestamp=1234567890,
            transaction_count=2000,
            blockchain=self.blockchain
        )
    
    async def get_current_block_number(self) -> int:
        """Get current Bitcoin block number"""
        return 800000
    
    async def get_address_balance(self, address: str, asset: str = None) -> Decimal:
        """Get Bitcoin address balance"""
        return Decimal("0.1")


class BlockchainFactory:
    """Factory for creating blockchain interfaces"""
    
    @staticmethod
    def create_interface(blockchain: BlockchainNetwork, config: BlockchainConfig) -> BlockchainInterface:
        """Create appropriate blockchain interface"""
        
        if blockchain == BlockchainNetwork.ETHEREUM:
            return EthereumInterface(config)
        elif blockchain == BlockchainNetwork.BITCOIN:
            return BitcoinInterface(config)
        elif blockchain == BlockchainNetwork.BINANCE_SMART_CHAIN:
            # BSC uses same interface as Ethereum (EVM compatible)
            interface = EthereumInterface(config)
            interface.blockchain = BlockchainNetwork.BINANCE_SMART_CHAIN
            return interface
        elif blockchain == BlockchainNetwork.POLYGON:
            # Polygon uses same interface as Ethereum (EVM compatible)
            interface = EthereumInterface(config)
            interface.blockchain = BlockchainNetwork.POLYGON
            return interface
        # Add more blockchain interfaces as needed
        else:
            raise ValueError(f"Unsupported blockchain: {blockchain}")


class BlockchainConfigManager:
    """Manages blockchain configuration from environment variables"""
    
    @staticmethod
    def load_from_env() -> Dict[BlockchainNetwork, BlockchainConfig]:
        """Load blockchain configurations from environment variables"""
        configs = {}
        
        # Ethereum configuration
        if os.getenv('ETHEREUM_RPC_URL'):
            configs[BlockchainNetwork.ETHEREUM] = BlockchainConfig(
                rpc_url=os.getenv('ETHEREUM_RPC_URL'),
                api_key=os.getenv('ETHEREUM_API_KEY'),
                rate_limit_per_second=int(os.getenv('ETHEREUM_RATE_LIMIT', '10'))
            )
        
        # Bitcoin configuration
        if os.getenv('BITCOIN_RPC_URL'):
            configs[BlockchainNetwork.BITCOIN] = BlockchainConfig(
                rpc_url=os.getenv('BITCOIN_RPC_URL'),
                rpc_user=os.getenv('BITCOIN_RPC_USER'),
                rpc_password=os.getenv('BITCOIN_RPC_PASSWORD'),
                rate_limit_per_second=int(os.getenv('BITCOIN_RATE_LIMIT', '5'))
            )
        
        # BSC configuration
        if os.getenv('BSC_RPC_URL'):
            configs[BlockchainNetwork.BINANCE_SMART_CHAIN] = BlockchainConfig(
                rpc_url=os.getenv('BSC_RPC_URL'),
                api_key=os.getenv('BSC_API_KEY'),
                rate_limit_per_second=int(os.getenv('BSC_RATE_LIMIT', '10'))
            )
        
        return configs
    
    @staticmethod
    def create_default_config() -> Dict[BlockchainNetwork, BlockchainConfig]:
        """Create default configuration for testing"""
        return {
            BlockchainNetwork.ETHEREUM: BlockchainConfig(
                rpc_url="https://mainnet.infura.io/v3/YOUR_KEY",
                rate_limit_per_second=10
            ),
            BlockchainNetwork.BITCOIN: BlockchainConfig(
                rpc_url="http://localhost:8332",
                rpc_user="bitcoin",
                rpc_password="password",
                rate_limit_per_second=5
            )
        }


class BlockchainManager:
    """Manages multiple blockchain interfaces"""
    
    def __init__(self, blockchain_configs: Dict[BlockchainNetwork, BlockchainConfig]):
        self.interfaces = {}
        self.configs = blockchain_configs
        
        # Initialize interfaces for configured blockchains
        for blockchain, config in blockchain_configs.items():
            try:
                self.interfaces[blockchain] = BlockchainFactory.create_interface(blockchain, config)
                print(f"Initialized {blockchain.value} interface")
            except Exception as e:
                print(f"Failed to initialize {blockchain.value} interface: {e}")
    
    async def verify_pattern_on_chain(self, pattern: DetectedPattern) -> PatternVerificationResult:
        """Verify pattern across relevant blockchains"""
        blockchain = BlockchainNetwork(pattern.blockchain)
        
        if blockchain not in self.interfaces:
            return PatternVerificationResult(
                pattern_id="unknown",
                is_valid=False,
                verification_timestamp=int(time.time()),
                addresses_exist=False,
                transactions_verified=0,
                total_transactions=len(pattern.transaction_graph.edges),
                verification_confidence=0.0,
                verification_errors=[f"No interface available for {blockchain.value}"]
            )
        
        interface = self.interfaces[blockchain]
        verification_result = PatternVerificationResult(
            pattern_id="unknown",
            is_valid=True,
            verification_timestamp=int(time.time()),
            addresses_exist=True,
            transactions_verified=0,
            total_transactions=len(pattern.transaction_graph.edges),
            verification_confidence=0.0,
            verification_errors=[],
            suspicious_flags=[]
        )
        
        # Verify each transaction in the pattern
        for edge in pattern.transaction_graph.edges:
            try:
                # Verify transaction exists
                tx = await interface.get_transaction(edge.transaction_hash)
                if tx is None:
                    verification_result.verification_errors.append(f"Transaction {edge.transaction_hash} not found")
                    verification_result.is_valid = False
                    continue
                
                # Verify transaction details match
                if not self._verify_transaction_details(edge, tx):
                    verification_result.verification_errors.append(f"Transaction {edge.transaction_hash} details mismatch")
                    verification_result.is_valid = False
                    continue
                
                verification_result.transactions_verified += 1
                
            except Exception as e:
                verification_result.verification_errors.append(f"Error verifying {edge.transaction_hash}: {str(e)}")
                verification_result.is_valid = False
        
        # Verify addresses exist
        all_addresses = set()
        for node in pattern.transaction_graph.nodes:
            all_addresses.add(node.address)
        
        for address in all_addresses:
            try:
                exists = await interface.verify_address_exists(address)
                if not exists:
                    verification_result.verification_errors.append(f"Address {address} does not exist")
                    verification_result.addresses_exist = False
            except Exception as e:
                verification_result.verification_errors.append(f"Error verifying address {address}: {str(e)}")
        
        # Calculate verification confidence
        if verification_result.total_transactions > 0:
            verification_result.verification_confidence = (
                verification_result.transactions_verified / verification_result.total_transactions
            )
        
        return verification_result
    
    def _verify_transaction_details(self, edge: GraphEdge, tx: Transaction) -> bool:
        """Verify transaction details match between pattern and blockchain"""
        # Check addresses match
        if edge.from_address.lower() != tx.from_address.lower():
            return False
        if edge.to_address.lower() != tx.to_address.lower():
            return False
        
        # Check amounts match (with small tolerance for precision)
        amount_diff = abs(edge.amount - tx.amount)
        if amount_diff > Decimal('0.000001'):  # 1e-6 tolerance
            return False
        
        # Check timestamps are reasonable (within 1 hour)
        time_diff = abs(edge.timestamp - tx.timestamp)
        if time_diff > 3600:  # 1 hour tolerance
            return False
        
        return True
    
    def get_supported_blockchains(self) -> List[BlockchainNetwork]:
        """Get list of supported blockchains"""
        return list(self.interfaces.keys())
    
    def is_blockchain_supported(self, blockchain: str) -> bool:
        """Check if blockchain is supported"""
        try:
            blockchain_enum = BlockchainNetwork(blockchain)
            return blockchain_enum in self.interfaces
        except ValueError:
            return False


@dataclass
class ComprehensiveVerificationResult:
    """Complete verification result including all checks"""
    basic_verification: PatternVerificationResult
    blockchain_coverage: Dict[str, bool]
    overall_confidence: float
    
    def is_fully_verified(self) -> bool:
        """Check if pattern is fully verified"""
        return (self.basic_verification.is_valid and 
                self.overall_confidence > 0.8)


class PatternBlockchainVerifier:
    """Integrates pattern verification with blockchain interfaces"""
    
    def __init__(self, blockchain_manager: BlockchainManager):
        self.blockchain_manager = blockchain_manager
    
    async def comprehensive_pattern_verification(
        self, 
        pattern: DetectedPattern
    ) -> ComprehensiveVerificationResult:
        """Perform comprehensive blockchain verification of pattern"""
        
        # Basic on-chain verification
        basic_verification = await self.blockchain_manager.verify_pattern_on_chain(pattern)
        
        # Check blockchain coverage
        blockchain_coverage = {
            pattern.blockchain: self.blockchain_manager.is_blockchain_supported(pattern.blockchain)
        }
        
        # Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(basic_verification, blockchain_coverage)
        
        return ComprehensiveVerificationResult(
            basic_verification=basic_verification,
            blockchain_coverage=blockchain_coverage,
            overall_confidence=overall_confidence
        )
    
    def _calculate_overall_confidence(
        self, 
        basic_verification: PatternVerificationResult, 
        blockchain_coverage: Dict[str, bool]
    ) -> float:
        """Calculate overall confidence score"""
        if not basic_verification.is_valid:
            return 0.0
        
        # Base confidence from verification
        base_confidence = basic_verification.verification_confidence
        
        # Penalty if blockchain not supported
        coverage_penalty = 0.0 if all(blockchain_coverage.values()) else 0.2
        
        return max(0.0, base_confidence - coverage_penalty)