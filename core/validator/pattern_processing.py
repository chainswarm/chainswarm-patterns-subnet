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

import time
from dataclasses import dataclass, field
from typing import List, Dict, Any

from core.protocol import DetectedPattern, PatternType, TransactionGraph


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
class PatternVerificationResult:
    """Results of on-chain pattern verification"""
    pattern_id: str
    is_valid: bool
    verification_timestamp: int
    
    # Verification checks
    addresses_exist: bool
    transactions_verified: int
    total_transactions: int
    verification_confidence: float
    
    # Issues found
    verification_errors: List[str] = field(default_factory=list)
    suspicious_flags: List[str] = field(default_factory=list)
    
    def get_verification_score(self) -> float:
        """Calculate overall verification score"""
        if not self.is_valid:
            return 0.0
        return (self.transactions_verified / self.total_transactions) * self.verification_confidence


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


@dataclass
class StoredPattern:
    """
    Pattern as stored in Memgraph with complete validator metadata.
    
    This represents the final form of a pattern after all validator processing.
    """
    # Original miner data
    transaction_graph: TransactionGraph
    blockchain: str
    asset_symbol: str
    detection_timestamp: int
    
    # Validator additions
    pattern_id: str
    pattern_hash: str
    pattern_type: PatternType
    confidence_score: float
    
    # Scoring results
    pattern_score: float
    complexity_score: float
    uniqueness_score: float
    volume_significance: float
    recency_score: float
    
    # Verification metadata
    verification_status: str
    verification_confidence: float
    verification_errors: List[str] = field(default_factory=list)
    
    # Metadata
    miner_hotkey: str
    validator_hotkey: str
    classification_timestamp: int
    verification_timestamp: int
    
    # Anti-gaming data
    is_duplicate: bool = False
    similar_patterns: List[str] = field(default_factory=list)
    
    # Reputation impact
    miner_reputation_delta: float = 0.0


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