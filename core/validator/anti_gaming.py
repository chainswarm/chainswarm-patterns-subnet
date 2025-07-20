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

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

from core.protocol import DetectedPattern, TransactionGraph
from core.validator.pattern_processing import MinerReputation


@dataclass
class GraphSignature:
    """Structural signature of a transaction graph for similarity detection"""
    node_count: int
    edge_count: int
    max_degree: int
    cycle_count: int
    diameter: int
    clustering_coefficient: float
    degree_distribution: List[int]
    
    def similarity_score(self, other: 'GraphSignature') -> float:
        """Calculate similarity score between signatures"""
        # Normalize differences
        node_diff = abs(self.node_count - other.node_count) / max(self.node_count, other.node_count)
        edge_diff = abs(self.edge_count - other.edge_count) / max(self.edge_count, other.edge_count)
        degree_diff = abs(self.max_degree - other.max_degree) / max(self.max_degree, other.max_degree)
        
        # Calculate overall similarity
        similarity = 1.0 - (node_diff + edge_diff + degree_diff) / 3.0
        return max(0.0, similarity)


@dataclass
class DiscoveryRegistrationResult:
    """Result of pattern discovery registration for first-discovery rule"""
    is_first_discovery: bool
    is_within_grace_period: bool
    first_discoverer: str
    discovery_timestamp: int
    credit_multiplier: float  # 0.0 = no credit, 0.5 = partial, 1.0 = full


@dataclass
class GamingAnalysisResult:
    """Result of comprehensive gaming analysis"""
    gaming_flags: List[str]
    confidence_scores: Dict[str, float]
    overall_gaming_probability: float
    recommended_action: str  # "accept", "reject", "flag_for_review"
    
    def should_reject_pattern(self) -> bool:
        """Determine if pattern should be rejected"""
        return self.overall_gaming_probability > 0.8 or "coordination_detected" in self.gaming_flags


@dataclass
class AddressAgeAnalysis:
    """Analysis of address ages in pattern"""
    new_address_count: int
    total_address_count: int
    suspicious_new_address_ratio: float
    is_suspicious: bool
    confidence: float


@dataclass
class ComplexityAuthenticityAnalysis:
    """Analysis of pattern complexity authenticity"""
    circular_ratio: float
    dust_ratio: float
    temporal_clustering: float
    round_number_bias: float
    is_artificially_complex: bool
    confidence: float


@dataclass
class CoordinationAnalysis:
    """Analysis of coordination between miners"""
    coordination_indicators: List[str]
    has_coordination_indicators: bool
    confidence: float


class PatternDeduplicationEngine:
    """Advanced pattern deduplication using graph similarity algorithms"""
    
    def __init__(self):
        self.similarity_threshold = 0.85  # 85% similarity = duplicate
        self.stored_pattern_hashes = {}   # Quick hash lookup
        self.graph_signatures = {}        # Graph structural signatures
    
    def is_duplicate_pattern(self, new_pattern: DetectedPattern) -> Tuple[bool, List[str]]:
        """Check if pattern is duplicate of existing patterns"""
        
        # Level 1: Quick hash check
        pattern_hash = self._calculate_pattern_hash(new_pattern)
        if pattern_hash in self.stored_pattern_hashes:
            return True, [self.stored_pattern_hashes[pattern_hash]]
        
        # Level 2: Graph signature similarity
        graph_signature = self._calculate_graph_signature(new_pattern)
        similar_patterns = self._find_similar_signatures(graph_signature)
        
        # Level 3: Detailed graph isomorphism for close matches
        for similar_pattern_id in similar_patterns:
            similarity_score = self._calculate_detailed_similarity(new_pattern, similar_pattern_id)
            if similarity_score > self.similarity_threshold:
                return True, [similar_pattern_id]
        
        return False, []
    
    def _calculate_pattern_hash(self, pattern: DetectedPattern) -> str:
        """Calculate quick hash for exact duplicate detection"""
        # Normalize addresses and amounts for consistent hashing
        normalized_edges = []
        for edge in pattern.transaction_graph.edges:
            normalized_edges.append((
                edge.from_address.lower(),
                edge.to_address.lower(),
                str(edge.amount),
                edge.timestamp
            ))
        
        # Sort for consistent ordering
        normalized_edges.sort()
        hash_input = json.dumps(normalized_edges, sort_keys=True)
        return hashlib.sha256(hash_input.encode()).hexdigest()
    
    def _calculate_graph_signature(self, pattern: DetectedPattern) -> GraphSignature:
        """Calculate structural signature for similarity detection"""
        graph = pattern.transaction_graph
        
        return GraphSignature(
            node_count=len(graph.nodes),
            edge_count=len(graph.edges),
            max_degree=self._calculate_max_degree(graph),
            cycle_count=self._count_cycles(graph),
            diameter=self._calculate_diameter(graph),
            clustering_coefficient=self._calculate_clustering(graph),
            degree_distribution=self._calculate_degree_distribution(graph)
        )
    
    def _find_similar_signatures(self, signature: GraphSignature) -> List[str]:
        """Find patterns with similar graph signatures"""
        similar_patterns = []
        
        for pattern_id, stored_signature in self.graph_signatures.items():
            similarity = signature.similarity_score(stored_signature)
            if similarity > 0.7:  # Threshold for detailed analysis
                similar_patterns.append(pattern_id)
        
        return similar_patterns
    
    def _calculate_detailed_similarity(self, pattern1: DetectedPattern, pattern2_id: str) -> float:
        """Calculate detailed similarity between two patterns"""
        # This would load pattern2 from storage and compare
        # For now, return a placeholder
        return 0.0
    
    def _calculate_max_degree(self, graph: TransactionGraph) -> int:
        """Calculate maximum degree in the graph"""
        degree_count = {}
        
        for edge in graph.edges:
            degree_count[edge.from_address] = degree_count.get(edge.from_address, 0) + 1
            degree_count[edge.to_address] = degree_count.get(edge.to_address, 0) + 1
        
        return max(degree_count.values()) if degree_count else 0
    
    def _count_cycles(self, graph: TransactionGraph) -> int:
        """Count cycles in the graph"""
        # Simplified cycle counting
        visited = set()
        cycles = 0
        
        for node in graph.nodes:
            if node.address not in visited:
                cycles += self._dfs_cycle_count(graph, node.address, set(), visited)
        
        return cycles
    
    def _dfs_cycle_count(self, graph: TransactionGraph, address: str, path: set, global_visited: set) -> int:
        """DFS-based cycle counting"""
        if address in path:
            return 1
        
        if address in global_visited:
            return 0
        
        global_visited.add(address)
        path.add(address)
        
        cycles = 0
        outgoing_edges = graph.get_edges_from_address(address)
        
        for edge in outgoing_edges:
            cycles += self._dfs_cycle_count(graph, edge.to_address, path.copy(), global_visited)
        
        return cycles
    
    def _calculate_diameter(self, graph: TransactionGraph) -> int:
        """Calculate graph diameter (longest shortest path)"""
        # Simplified implementation
        return len(graph.nodes)
    
    def _calculate_clustering(self, graph: TransactionGraph) -> float:
        """Calculate clustering coefficient"""
        # Simplified implementation
        return 0.5
    
    def _calculate_degree_distribution(self, graph: TransactionGraph) -> List[int]:
        """Calculate degree distribution"""
        degree_count = {}
        
        for edge in graph.edges:
            degree_count[edge.from_address] = degree_count.get(edge.from_address, 0) + 1
            degree_count[edge.to_address] = degree_count.get(edge.to_address, 0) + 1
        
        # Return distribution as list
        max_degree = max(degree_count.values()) if degree_count else 0
        distribution = [0] * (max_degree + 1)
        
        for degree in degree_count.values():
            distribution[degree] += 1
        
        return distribution


class FirstDiscoveryEnforcement:
    """Enforce first-discovery rule for pattern rewards"""
    
    def __init__(self):
        self.discovery_registry = {}  # pattern_hash -> (miner_hotkey, timestamp)
        self.grace_period = 300       # 5 minutes grace period for network delays
    
    def register_pattern_discovery(
        self, 
        pattern: DetectedPattern, 
        miner_hotkey: str
    ) -> DiscoveryRegistrationResult:
        """Register pattern discovery and determine if miner gets credit"""
        
        pattern_hash = self._calculate_canonical_pattern_hash(pattern)
        current_time = int(time.time())
        
        # Check if pattern already discovered
        if pattern_hash in self.discovery_registry:
            first_discovery = self.discovery_registry[pattern_hash]
            time_diff = current_time - first_discovery['timestamp']
            
            # Within grace period - both miners get partial credit
            if time_diff <= self.grace_period:
                return DiscoveryRegistrationResult(
                    is_first_discovery=False,
                    is_within_grace_period=True,
                    first_discoverer=first_discovery['miner_hotkey'],
                    discovery_timestamp=first_discovery['timestamp'],
                    credit_multiplier=0.5  # Partial credit
                )
            else:
                # Too late - no credit
                return DiscoveryRegistrationResult(
                    is_first_discovery=False,
                    is_within_grace_period=False,
                    first_discoverer=first_discovery['miner_hotkey'],
                    discovery_timestamp=first_discovery['timestamp'],
                    credit_multiplier=0.0  # No credit
                )
        
        # First discovery - full credit
        self.discovery_registry[pattern_hash] = {
            'miner_hotkey': miner_hotkey,
            'timestamp': current_time
        }
        
        return DiscoveryRegistrationResult(
            is_first_discovery=True,
            is_within_grace_period=False,
            first_discoverer=miner_hotkey,
            discovery_timestamp=current_time,
            credit_multiplier=1.0  # Full credit
        )
    
    def _calculate_canonical_pattern_hash(self, pattern: DetectedPattern) -> str:
        """Calculate canonical hash that's invariant to minor variations"""
        # Normalize addresses to lowercase
        # Round amounts to remove minor precision differences
        # Sort transactions by timestamp then amount
        # Create hash from canonical representation
        
        normalized_edges = []
        for edge in pattern.transaction_graph.edges:
            normalized_edges.append((
                edge.from_address.lower(),
                edge.to_address.lower(),
                round(float(edge.amount), 6),  # Round to 6 decimal places
                edge.timestamp
            ))
        
        # Sort for consistent ordering
        normalized_edges.sort(key=lambda x: (x[3], x[2]))  # Sort by timestamp, then amount
        
        hash_input = json.dumps(normalized_edges, sort_keys=True)
        return hashlib.sha256(hash_input.encode()).hexdigest()


class AdvancedAntiGamingSystem:
    """Comprehensive anti-gaming detection and prevention"""
    
    def __init__(self):
        self.address_age_threshold = 30 * 24 * 3600  # 30 days in seconds
        self.coordination_detection_window = 3600    # 1 hour window
        self.pattern_farming_threshold = 5           # Max similar patterns per hour
    
    def comprehensive_gaming_analysis(
        self, 
        pattern: DetectedPattern, 
        miner_reputation: MinerReputation,
        recent_submissions: List[DetectedPattern]
    ) -> GamingAnalysisResult:
        """Comprehensive analysis for gaming detection"""
        
        gaming_flags = []
        confidence_scores = {}
        
        # 1. Address Age Analysis
        age_analysis = self._analyze_address_ages(pattern)
        if age_analysis.suspicious_new_address_ratio > 0.7:
            gaming_flags.append("suspicious_address_ages")
            confidence_scores["address_age"] = age_analysis.confidence
        
        # 2. Pattern Complexity Authenticity
        complexity_analysis = self._analyze_pattern_authenticity(pattern)
        if complexity_analysis.is_artificially_complex:
            gaming_flags.append("artificial_complexity")
            confidence_scores["complexity"] = complexity_analysis.confidence
        
        # 3. Coordination Detection
        coordination_analysis = self._detect_coordination(pattern, recent_submissions)
        if coordination_analysis.has_coordination_indicators:
            gaming_flags.append("coordination_detected")
            confidence_scores["coordination"] = coordination_analysis.confidence
        
        # 4. Pattern Farming Detection
        farming_analysis = self._detect_pattern_farming(pattern, miner_reputation, recent_submissions)
        if farming_analysis:
            gaming_flags.append("pattern_farming")
            confidence_scores["farming"] = 0.8
        
        return GamingAnalysisResult(
            gaming_flags=gaming_flags,
            confidence_scores=confidence_scores,
            overall_gaming_probability=self._calculate_overall_gaming_probability(confidence_scores),
            recommended_action=self._determine_recommended_action(gaming_flags, confidence_scores)
        )
    
    def _analyze_address_ages(self, pattern: DetectedPattern) -> AddressAgeAnalysis:
        """Analyze age distribution of addresses in pattern"""
        current_time = int(time.time())
        new_addresses = 0
        total_addresses = len(pattern.transaction_graph.nodes)
        
        # For now, assume all addresses are old (would need blockchain integration)
        new_address_ratio = 0.0
        
        return AddressAgeAnalysis(
            new_address_count=new_addresses,
            total_address_count=total_addresses,
            suspicious_new_address_ratio=new_address_ratio,
            is_suspicious=new_address_ratio > 0.7,
            confidence=new_address_ratio if new_address_ratio > 0.7 else 0.0
        )
    
    def _analyze_pattern_authenticity(self, pattern: DetectedPattern) -> ComplexityAuthenticityAnalysis:
        """Detect artificially inflated complexity"""
        graph = pattern.transaction_graph
        
        # Check for meaningless circular transactions
        circular_ratio = self._calculate_circular_transaction_ratio(graph)
        
        # Check for dust transactions (very small amounts)
        dust_ratio = self._calculate_dust_transaction_ratio(graph)
        
        # Check for temporal clustering (automated patterns)
        temporal_clustering = self._calculate_temporal_clustering(graph)
        
        # Check for round number bias (artificial amounts)
        round_number_bias = self._calculate_round_number_bias(graph)
        
        # Determine if artificially complex
        artificial_indicators = 0
        if circular_ratio > 0.5: artificial_indicators += 1
        if dust_ratio > 0.3: artificial_indicators += 1
        if temporal_clustering > 0.8: artificial_indicators += 1
        if round_number_bias > 0.6: artificial_indicators += 1
        
        is_artificial = artificial_indicators >= 2
        confidence = artificial_indicators / 4.0
        
        return ComplexityAuthenticityAnalysis(
            circular_ratio=circular_ratio,
            dust_ratio=dust_ratio,
            temporal_clustering=temporal_clustering,
            round_number_bias=round_number_bias,
            is_artificially_complex=is_artificial,
            confidence=confidence
        )
    
    def _detect_coordination(
        self, 
        pattern: DetectedPattern, 
        recent_submissions: List[DetectedPattern]
    ) -> CoordinationAnalysis:
        """Detect coordination between miners"""
        
        coordination_indicators = []
        
        # Check for similar submission timing
        submission_times = [p.detection_timestamp for p in recent_submissions]
        if self._has_suspicious_timing_correlation(submission_times):
            coordination_indicators.append("timing_correlation")
        
        # Check for overlapping address sets
        pattern_addresses = {node.address for node in pattern.transaction_graph.nodes}
        for other_pattern in recent_submissions:
            other_addresses = {node.address for node in other_pattern.transaction_graph.nodes}
            overlap_ratio = len(pattern_addresses & other_addresses) / len(pattern_addresses | other_addresses)
            if overlap_ratio > 0.5:
                coordination_indicators.append("address_overlap")
                break
        
        has_coordination = len(coordination_indicators) >= 1
        confidence = len(coordination_indicators) / 2.0
        
        return CoordinationAnalysis(
            coordination_indicators=coordination_indicators,
            has_coordination_indicators=has_coordination,
            confidence=confidence
        )
    
    def _detect_pattern_farming(
        self, 
        pattern: DetectedPattern, 
        miner_reputation: MinerReputation, 
        recent_submissions: List[DetectedPattern]
    ) -> bool:
        """Detect if miner is farming similar patterns"""
        # Check if miner has submitted too many similar patterns recently
        return len(recent_submissions) > self.pattern_farming_threshold
    
    def _calculate_circular_transaction_ratio(self, graph: TransactionGraph) -> float:
        """Calculate ratio of circular transactions"""
        # Simplified implementation
        return 0.2
    
    def _calculate_dust_transaction_ratio(self, graph: TransactionGraph) -> float:
        """Calculate ratio of dust transactions"""
        # Simplified implementation
        return 0.1
    
    def _calculate_temporal_clustering(self, graph: TransactionGraph) -> float:
        """Calculate temporal clustering score"""
        # Simplified implementation
        return 0.3
    
    def _calculate_round_number_bias(self, graph: TransactionGraph) -> float:
        """Calculate round number bias in amounts"""
        # Simplified implementation
        return 0.2
    
    def _has_suspicious_timing_correlation(self, timestamps: List[int]) -> bool:
        """Check for suspicious timing correlation"""
        # Simplified implementation
        return False
    
    def _calculate_overall_gaming_probability(self, confidence_scores: Dict[str, float]) -> float:
        """Calculate overall gaming probability"""
        if not confidence_scores:
            return 0.0
        
        # Average of all confidence scores
        return sum(confidence_scores.values()) / len(confidence_scores)
    
    def _determine_recommended_action(self, gaming_flags: List[str], confidence_scores: Dict[str, float]) -> str:
        """Determine recommended action based on gaming analysis"""
        overall_prob = self._calculate_overall_gaming_probability(confidence_scores)
        
        if overall_prob > 0.8 or "coordination_detected" in gaming_flags:
            return "reject"
        elif overall_prob > 0.5:
            return "flag_for_review"
        else:
            return "accept"


class RealTimeGamingPrevention:
    """Real-time prevention of gaming attempts"""
    
    def __init__(self):
        self.submission_rate_limits = {}  # miner_hotkey -> submission tracker
        self.pattern_similarity_cache = {}
        self.suspicious_miner_watchlist = set()
    
    def validate_submission_rate(self, miner_hotkey: str) -> bool:
        """Check if miner is submitting at suspicious rate"""
        current_time = int(time.time())
        
        if miner_hotkey not in self.submission_rate_limits:
            self.submission_rate_limits[miner_hotkey] = []
        
        # Clean old submissions (older than 1 hour)
        submissions = self.submission_rate_limits[miner_hotkey]
        submissions = [t for t in submissions if current_time - t < 3600]
        
        # Check rate limit (max 10 patterns per hour)
        if len(submissions) >= 10:
            return False
        
        # Add current submission
        submissions.append(current_time)
        self.submission_rate_limits[miner_hotkey] = submissions
        
        return True
    
    def add_to_watchlist(self, miner_hotkey: str, reason: str):
        """Add miner to suspicious activity watchlist"""
        self.suspicious_miner_watchlist.add(miner_hotkey)
        # Log the reason and timestamp
        
    def is_on_watchlist(self, miner_hotkey: str) -> bool:
        """Check if miner is on suspicious activity watchlist"""
        return miner_hotkey in self.suspicious_miner_watchlist