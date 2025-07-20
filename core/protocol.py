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


# Validator-side data structures (not transmitted via synapse)
# These are used internally by validators for processing patterns

@dataclass
class ClassifiedPattern:
    """
    Pattern after validator classification and analysis.
    
    This extends the basic DetectedPattern with validator-added metadata.
    """
    # Original miner data
    detected_pattern: DetectedPattern
    
    # Validator additions
    pattern_id: str
    pattern_hash: str
    pattern_type: PatternType
    confidence_score: float
    
    # Scoring components
    complexity_score: float
    uniqueness_score: float
    volume_significance: float
    recency_score: float
    
    # Verification results
    verification_status: str  # "verified", "failed", "pending"
    verification_confidence: float
    verification_errors: List[str] = field(default_factory=list)
    
    # Metadata
    miner_hotkey: str
    validator_hotkey: str
    classification_timestamp: int
    
    def get_final_score(self) -> float:
        """Calculate the final weighted score for this pattern"""
        # Scoring weights from specification
        weights = {
            'classification': 0.25,
            'complexity': 0.30,
            'recency': 0.20,
            'volume': 0.15,
            'uniqueness': 0.10
        }
        
        # Calculate weighted score
        score = (
            self.confidence_score * weights['classification'] +
            self.complexity_score * weights['complexity'] +
            self.recency_score * weights['recency'] +
            self.volume_significance * weights['volume'] +
            self.uniqueness_score * weights['uniqueness']
        )
        
        return min(1.0, max(0.0, score))  # Clamp between 0-1


@dataclass
class MinerReputation:
    """
    Tracks miner reputation and performance metrics.
    
    Used by validators to calculate reputation multipliers for pattern scoring.
    """
    miner_hotkey: str
    
    # Basic statistics
    total_patterns_submitted: int = 0
    verified_patterns: int = 0
    rejected_patterns: int = 0
    
    # Quality metrics
    average_pattern_score: float = 0.0
    average_complexity_score: float = 0.0
    verification_success_rate: float = 0.0
    
    # Anti-gaming metrics
    historical_pattern_ratio: float = 0.5  # Ratio of historical vs recent patterns
    duplicate_submission_count: int = 0
    gaming_penalty_score: float = 0.0
    
    # Reputation scores
    base_reputation_score: float = 1.0
    reputation_multiplier: float = 1.0
    
    # Timestamps
    first_submission_timestamp: int = 0
    last_submission_timestamp: int = 0
    reputation_update_timestamp: int = 0
    
    def update_with_pattern(self, pattern: ClassifiedPattern):
        """Update reputation based on a new pattern submission"""
        self.total_patterns_submitted += 1
        self.last_submission_timestamp = int(time.time())
        
        if pattern.verification_status == "verified":
            self.verified_patterns += 1
            # Update running averages
            self._update_running_average('average_pattern_score', pattern.get_final_score())
            self._update_running_average('average_complexity_score', pattern.complexity_score)
        else:
            self.rejected_patterns += 1
        
        # Update verification success rate
        if self.total_patterns_submitted > 0:
            self.verification_success_rate = self.verified_patterns / self.total_patterns_submitted
        
        # Recalculate reputation multiplier
        self._calculate_reputation_multiplier()
        
        self.reputation_update_timestamp = int(time.time())
    
    def _update_running_average(self, field_name: str, new_value: float):
        """Update a running average field"""
        current_value = getattr(self, field_name)
        # Simple exponential moving average with alpha=0.1
        alpha = 0.1
        new_average = alpha * new_value + (1 - alpha) * current_value
        setattr(self, field_name, new_average)
    
    def _calculate_reputation_multiplier(self):
        """Calculate the reputation multiplier applied to pattern scores"""
        multiplier = self.base_reputation_score
        
        # Penalty for poor historical/recent balance
        if self.historical_pattern_ratio < 0.3:  # Less than 30% historical
            balance_penalty = 0.5 * (0.3 - self.historical_pattern_ratio)
            multiplier -= balance_penalty
        
        # Penalty for gaming attempts
        gaming_penalty = min(0.8, self.duplicate_submission_count * 0.1 + self.gaming_penalty_score)
        multiplier -= gaming_penalty
        
        # Bonus for consistent quality
        if (self.verification_success_rate > 0.9 and 
            self.average_pattern_score > 0.7 and
            self.total_patterns_submitted > 50):
            multiplier += 0.3
        elif (self.verification_success_rate > 0.8 and 
              self.average_pattern_score > 0.6):
            multiplier += 0.1
        
        # Clamp between 0.1 and 2.0
        self.reputation_multiplier = max(0.1, min(2.0, multiplier))


# Helper functions for pattern analysis

def calculate_pattern_complexity(graph: TransactionGraph) -> float:
    """
    Calculate complexity score for a transaction pattern.
    
    Args:
        graph: The transaction graph to analyze
        
    Returns:
        Complexity score between 0.0 and 1.0
    """
    if not graph.edges:
        return 0.0
    
    # Basic metrics
    node_count = len(graph.nodes)
    edge_count = len(graph.edges)
    unique_addresses = len(graph.get_unique_addresses())
    
    # Calculate graph depth (longest path)
    graph_depth = _calculate_graph_depth(graph)
    
    # Calculate branching factor
    branching_factor = edge_count / node_count if node_count > 0 else 0
    
    # Detect cycles
    cycle_count = _count_cycles(graph)
    
    # Base complexity from graph structure
    base_score = min(1.0, (graph_depth * unique_addresses) / 100.0)
    
    # Bonuses for sophisticated patterns
    cycle_bonus = min(0.3, cycle_count * 0.1)
    branching_bonus = min(0.2, branching_factor * 0.1)
    
    total_score = base_score + cycle_bonus + branching_bonus
    return min(1.0, total_score)


def _calculate_graph_depth(graph: TransactionGraph) -> int:
    """Calculate the maximum depth (longest path) in the transaction graph"""
    # Simple implementation - could be enhanced with proper graph algorithms
    max_depth = 0
    
    # For each node, try to find the longest path starting from it
    for node in graph.nodes:
        depth = _dfs_max_depth(graph, node.address, set())
        max_depth = max(max_depth, depth)
    
    return max_depth


def _dfs_max_depth(graph: TransactionGraph, address: str, visited: set) -> int:
    """DFS to find maximum depth from a given address"""
    if address in visited:
        return 0
    
    visited.add(address)
    max_depth = 0
    
    # Find all outgoing edges from this address
    outgoing_edges = graph.get_edges_from_address(address)
    
    for edge in outgoing_edges:
        depth = 1 + _dfs_max_depth(graph, edge.to_address, visited.copy())
        max_depth = max(max_depth, depth)
    
    return max_depth


def _count_cycles(graph: TransactionGraph) -> int:
    """Count the number of cycles in the transaction graph"""
    # Simple cycle detection - could be enhanced
    cycles = 0
    visited = set()
    
    for node in graph.nodes:
        if node.address not in visited:
            cycles += _dfs_cycle_detection(graph, node.address, set(), visited)
    
    return cycles


def _dfs_cycle_detection(graph: TransactionGraph, address: str, path: set, global_visited: set) -> int:
    """DFS-based cycle detection"""
    if address in path:
        return 1  # Found a cycle
    
    if address in global_visited:
        return 0
    
    global_visited.add(address)
    path.add(address)
    
    cycles = 0
    outgoing_edges = graph.get_edges_from_address(address)
    
    for edge in outgoing_edges:
        cycles += _dfs_cycle_detection(graph, edge.to_address, path.copy(), global_visited)
    
    return cycles


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
