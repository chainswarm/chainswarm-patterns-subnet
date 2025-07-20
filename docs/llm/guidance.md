# Coding Agent Guidance

Read these instructions to get better understanding of what you have to do:

## Project Overview
You are building a Bittensor subnet for detecting malicious transaction patterns across various blockchains. The subnet focuses on identifying suspicious fraudulent network activities through distributed pattern detection.

## Core Architecture

### 1) Miner Role
- **Primary Task**: Detect suspicious transaction patterns on blockchain networks
- **Starting Point**: Empty template with defined data contract/synapses
- **Pattern Types to Detect**: 
  - Smurfing (breaking large transactions into smaller ones)
  - Layering (complex chains of transactions to obscure origin)
  - Circular transfers (tokens moving in loops)
  - Wash trading patterns
  - Mixer/tumbler activities
  - Other emerging fraud patterns
- **Output**: Submit detected patterns to validators with supporting evidence

### 2) Validator Role
- **Verification Process**: 
  - Use blockchain nodes to verify address existence
  - Confirm transaction history and volumes
  - Validate connections between addresses exist on-chain
  - Check pattern data integrity and completeness
- **Scoring Mechanism**: Evaluate patterns based on:
  - **Classification accuracy**: Correct categorization (smurfing, layering, cyclic transfer, etc.)
  - **Pattern complexity**: Complex multi-hop, multi-asset patterns score higher than simple patterns
  - **Data recency balance**: Recent patterns valued for ongoing fraud detection, but miner reputation considers historical pattern ratio
  - **Volume significance**: Transaction amounts and frequency
  - **Pattern uniqueness**: First discoverer wins - no duplicate scoring for same patterns
- **Registry Management**: Store miner hotkeys, detected patterns, and classification labels

### 3) Anti-Gaming Measures
- **Miner Reputation System**: 
  - Track each miner's historical vs recent pattern detection ratio
  - Miners submitting only recent patterns (potentially forged) receive reputation penalties
  - Reputation score affects overall pattern scoring weight
- **Pattern Complexity Scoring**: 
  - Simple circular patterns (A→B→A) receive lower scores
  - Complex multi-hop, multi-asset, sophisticated schemes receive higher scores
  - Real fraud typically involves layered complexity that's harder to fake
- **First-Discovery Rule**: 
  - Only the first miner to submit a specific pattern receives scoring
  - Duplicate pattern submissions receive zero points
  - Prevents coordination between miners sharing findings
- **Pattern Uniqueness Verification**: 
  - Use graph similarity algorithms to detect pattern variations
  - Heavily penalize near-duplicate submissions
- **Address Age & Activity Analysis**:
  - Patterns involving newly created address clusters are flagged as suspicious
  - Higher scores for patterns with established addresses and long transaction histories

## Business Value & Purpose
- **Resource Optimization**: Distributed pattern detection reduces computational costs
- **ML/LLM Training Data**: High-quality labeled fraud patterns for model training
- **Real-time Detection**: Enable chainswarm real-time malicious behavior detection for ongoing scams
- **Scalability**: Support pattern detection across 20+ blockchains
- **Miner-Friendly Design**: Rewards genuine value creation and pattern discovery innovation

## Technical Implementation Focus
- **Validation Logic**: Robust on-chain verification systems
- **Scoring Algorithms**: Multi-factor pattern evaluation emphasizing complexity and authenticity
- **Pattern Classification**: Accurate fraud type identification
- **Reputation Tracking**: Long-term miner behavior analysis
- **Pattern Deduplication**: Efficient duplicate detection and first-discovery enforcement
- **Integration**: Connect with chainswarm insights and analysis tools

## Key Success Metrics
- Pattern detection accuracy and complexity
- Miner reputation distribution (historical vs recent pattern balance)
- Pattern uniqueness and innovation
- Real-time fraud detection capability
- Integration success with downstream ML/analysis systems
    


# Project structure
@core here we put production code, ignore @template
@/core/protocol.py here we define data contracts to exchange data between valdiator and the miner
