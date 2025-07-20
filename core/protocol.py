# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
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

import time
import typing
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Dict, Any

import bittensor as bt

# Chainswarm Patterns Subnet Protocol
# This protocol enables distributed detection of malicious transaction patterns across blockchains.
# Miners detect suspicious patterns and submit them as transaction graphs to validators.
# Validators verify, classify, score, and store patterns for fraud detection and ML training.

# ---- Communication Flow ----
# 1. Validator queries miner: "Do you have any new patterns?"
# 2. Miner responds with detected transaction graphs (if any)
# 3. Validator verifies patterns on-chain, classifies, scores, and stores
# 4. Validator updates miner reputation based on pattern quality

# ---- Usage Examples ----

# Validator side:
#   query = PatternQuery()
#   response = await dendrite.query(axons=[miner_axon], synapse=query)
#   patterns = response.deserialize()  # Returns List[DetectedPattern]

# Miner side:
#   def handle_pattern_query(synapse: PatternQuery) -> PatternQuery:
#       synapse.detected_patterns = self.get_new_patterns()
#       return synapse
#   axon = bt.axon().attach(handle_pattern_query).serve(netuid=...).start()


class PatternType(Enum):
    """Types of malicious transaction patterns that can be detected"""
    SMURFING = "smurfing"                    # Breaking large transactions into smaller ones
    LAYERING = "layering"                    # Complex chains to obscure transaction origin
    CIRCULAR_TRANSFER = "circular_transfer"   # Tokens moving in loops
    WASH_TRADING = "wash_trading"            # Artificial volume creation
    MIXER_TUMBLER = "mixer_tumbler"          # Privacy coin mixing patterns
    SUSPICIOUS_VOLUME = "suspicious_volume"   # Unusual volume patterns
    RAPID_FIRE = "rapid_fire"                # High-frequency micro-transactions
    CUSTOM = "custom"                        # Novel emerging patterns


@dataclass
class GraphNode:
    """
    Represents a blockchain address in the transaction graph.
    
    Attributes:
        address: The blockchain address (e.g., Ethereum address, Bitcoin address)
        node_type: Type of address ("eoa", "contract", "exchange", "mixer", "unknown")
        metadata: Additional information about the address
    """
    address: str
    node_type: str  # "eoa", "contract", "exchange", "mixer", "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphEdge:
    """
    Represents a transaction between two addresses in the graph.
    
    Attributes:
        from_address: Source address of the transaction
        to_address: Destination address of the transaction
        amount: Transaction amount in the asset's base unit
        transaction_hash: Blockchain transaction hash for verification
        timestamp: Unix timestamp when transaction occurred
        metadata: Additional transaction information (gas fees, block number, etc.)
    """
    from_address: str
    to_address: str
    amount: Decimal
    transaction_hash: str
    timestamp: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TransactionGraph:
    """
    Graph structure representing a pattern of connected transactions.
    
    The graph consists of nodes (blockchain addresses) connected by edges (transactions).
    This structure allows for sophisticated analysis of transaction patterns and relationships.
    
    Attributes:
        nodes: List of addresses involved in the pattern
        edges: List of transactions connecting the addresses
    """
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    
    def get_node_by_address(self, address: str) -> Optional[GraphNode]:
        """Get a node by its address"""
        for node in self.nodes:
            if node.address == address:
                return node
        return None
    
    def get_edges_from_address(self, address: str) -> List[GraphEdge]:
        """Get all outgoing edges from an address"""
        return [edge for edge in self.edges if edge.from_address == address]
    
    def get_edges_to_address(self, address: str) -> List[GraphEdge]:
        """Get all incoming edges to an address"""
        return [edge for edge in self.edges if edge.to_address == address]
    
    def get_total_volume(self) -> Decimal:
        """Calculate total transaction volume in the pattern"""
        return sum(edge.amount for edge in self.edges)
    
    def get_unique_addresses(self) -> set:
        """Get all unique addresses in the pattern"""
        addresses = set()
        for edge in self.edges:
            addresses.add(edge.from_address)
            addresses.add(edge.to_address)
        return addresses


@dataclass
class DetectedPattern:
    """
    Raw pattern detected by a miner.
    
    Miners submit minimal data - just the transaction graph and basic context.
    Validators add classification, scoring, IDs, and all other metadata.
    
    Attributes:
        transaction_graph: The graph structure of connected transactions
        blockchain: Which blockchain the pattern was detected on
        asset_symbol: The asset involved in the pattern (e.g., "ETH", "BTC", "USDT")
        detection_timestamp: When the miner detected this pattern
    """
    transaction_graph: TransactionGraph
    blockchain: str
    asset_symbol: str
    detection_timestamp: int
    
    def __post_init__(self):
        """Validate the pattern data"""
        if not self.transaction_graph.nodes:
            raise ValueError("Pattern must have at least one node")
        if not self.transaction_graph.edges:
            raise ValueError("Pattern must have at least one edge")
        if not self.blockchain:
            raise ValueError("Blockchain must be specified")
        if not self.asset_symbol:
            raise ValueError("Asset symbol must be specified")


class PatternQuery(bt.Synapse):
    """
    Primary communication synapse for pattern detection queries.
    
    This synapse handles the simple query-response pattern:
    1. Validator sends empty query to miner
    2. Miner fills detected_patterns with any new patterns found
    3. Validator processes the patterns
    
    The design is intentionally minimal - miners only submit raw transaction graphs,
    and validators handle all the complex processing (classification, scoring, verification).
    
    Attributes:
        query_timestamp: When the validator sent the query
        detected_patterns: List of patterns detected by the miner (filled by miner)
    """

    # miners patter id, defined individually on the miner side, used for sending back ACKs
    pattern_id: str

    # Request fields (filled by validator)
    query_timestamp: int = field(default_factory=lambda: int(time.time()))
    
    # Response fields (filled by miner)
    detected_patterns: Optional[List[DetectedPattern]] = None
    
    def deserialize(self) -> List[DetectedPattern]:
        """
        Deserialize the response from the miner.
        
        Returns:
            List of detected patterns, or empty list if none found
            
        Example:
            >>> query = PatternQuery()
            >>> response = await dendrite.query(axons=[miner], synapse=query)
            >>> patterns = response.deserialize()
            >>> print(f"Received {len(patterns)} patterns")
        """
        return self.detected_patterns or []
    
    def has_patterns(self) -> bool:
        """Check if the miner found any patterns"""
        return bool(self.detected_patterns)
    
    def get_pattern_count(self) -> int:
        """Get the number of patterns detected"""
        return len(self.detected_patterns) if self.detected_patterns else 0

class PatternQueryAck(bt.Synapse):
    pattern_id: str

    def deserialize(self):
        return self.pattern_id


def create_sample_pattern() -> DetectedPattern:
    """
    Create a sample pattern for testing purposes.
    
    Returns:
        A sample DetectedPattern representing a simple circular transfer
    """
    # Create sample nodes
    nodes = [
        GraphNode(address="0x1234...abcd", node_type="eoa"),
        GraphNode(address="0x5678...efgh", node_type="eoa"),
        GraphNode(address="0x9abc...ijkl", node_type="contract")
    ]
    
    # Create sample edges (circular pattern)
    edges = [
        GraphEdge(
            from_address="0x1234...abcd",
            to_address="0x5678...efgh",
            amount=Decimal("100.0"),
            transaction_hash="0xabc123...",
            timestamp=int(time.time()) - 3600
        ),
        GraphEdge(
            from_address="0x5678...efgh",
            to_address="0x9abc...ijkl",
            amount=Decimal("95.0"),
            transaction_hash="0xdef456...",
            timestamp=int(time.time()) - 3000
        ),
        GraphEdge(
            from_address="0x9abc...ijkl",
            to_address="0x1234...abcd",
            amount=Decimal("90.0"),
            transaction_hash="0xghi789...",
            timestamp=int(time.time()) - 1800
        )
    ]
    
    # Create transaction graph
    graph = TransactionGraph(nodes=nodes, edges=edges)
    
    # Create detected pattern
    return DetectedPattern(
        transaction_graph=graph,
        blockchain="ethereum",
        asset_symbol="ETH",
        detection_timestamp=int(time.time())
    )
