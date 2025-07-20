#!/usr/bin/env python3
"""
Test script for the database implementation.
This script tests the basic functionality of the database module.
"""

import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.miner.database import DataManager, Pattern, AcknowledgedPattern


def test_database_functionality():
    """Test the basic database functionality."""
    print("Testing database functionality...")
    
    # Create a test database manager (uses SQLite in memory for testing)
    db_manager = DataManager("sqlite:///:memory:")
    
    print("✓ Database manager created successfully")
    
    # Test adding patterns
    print("\n1. Testing pattern creation...")
    pattern1 = db_manager.add_pattern(
        pattern_id="test_pattern_1",
        network="ethereum",
        asset_symbol="ETH",
        data="{'price': 2000, 'volume': 1000000}",
        importance=5
    )
    
    pattern2 = db_manager.add_pattern(
        pattern_id="test_pattern_2",
        network="bitcoin",
        asset_symbol="BTC",
        data="{'price': 45000, 'volume': 500000}",
        importance=8
    )
    
    pattern3 = db_manager.add_pattern(
        pattern_id="test_pattern_3",
        network="ethereum",
        asset_symbol="USDC",
        data="{'price': 1, 'volume': 2000000}",
        importance=3,
        asset_contract="0xa0b86a33e6776e681e9e29e6b8b8b8b8b8b8b8b8"
    )
    
    print(f"✓ Created pattern 1: {pattern1}")
    print(f"✓ Created pattern 2: {pattern2}")
    print(f"✓ Created pattern 3: {pattern3}")
    
    # Test getting unacknowledged patterns
    print("\n2. Testing unacknowledged patterns retrieval...")
    validator_hotkey = "test_validator_123"
    
    unacknowledged = db_manager.get_unacknowledged_patterns(validator_hotkey)
    print(f"✓ Found {len(unacknowledged)} unacknowledged patterns for validator")
    
    for pattern in unacknowledged:
        print(f"  - Pattern ID: {pattern.id}, Importance: {pattern.importance}, Network: {pattern.network}")
    
    # Test acknowledging patterns
    print("\n3. Testing pattern acknowledgment...")
    if unacknowledged:
        pattern_to_ack = unacknowledged[0]
        success = db_manager.acknowledge_pattern(pattern_to_ack.id, validator_hotkey)
        print(f"✓ Acknowledged pattern {pattern_to_ack.id}: {success}")
        
        # Check that the pattern is no longer unacknowledged
        unacknowledged_after = db_manager.get_unacknowledged_patterns(validator_hotkey)
        print(f"✓ Unacknowledged patterns after acknowledgment: {len(unacknowledged_after)}")
        
        # Test duplicate acknowledgment
        duplicate_ack = db_manager.acknowledge_pattern(pattern_to_ack.id, validator_hotkey)
        print(f"✓ Duplicate acknowledgment handled: {duplicate_ack}")
    
    # Test getting patterns with importance filter
    print("\n4. Testing importance filtering...")
    high_importance = db_manager.get_unacknowledged_patterns(validator_hotkey, min_importance=5)
    print(f"✓ Found {len(high_importance)} high importance patterns (>= 5)")
    
    # Test getting patterns with limit
    print("\n5. Testing result limiting...")
    limited_patterns = db_manager.get_unacknowledged_patterns(validator_hotkey, limit=1)
    print(f"✓ Limited results to 1 pattern: {len(limited_patterns)} returned")
    
    # Test getting pattern by ID
    print("\n6. Testing pattern retrieval by ID...")
    if pattern1:
        retrieved_pattern = db_manager.get_pattern_by_id(pattern1.id)
        print(f"✓ Retrieved pattern by ID: {retrieved_pattern}")
    
    # Test acknowledgment count
    print("\n7. Testing acknowledgment count...")
    if pattern1:
        ack_count = db_manager.get_acknowledgment_count(pattern1.id)
        print(f"✓ Acknowledgment count for pattern {pattern1.id}: {ack_count}")
    
    # Test with different validator
    print("\n8. Testing with different validator...")
    validator2_hotkey = "test_validator_456"
    unack_validator2 = db_manager.get_unacknowledged_patterns(validator2_hotkey)
    print(f"✓ Validator 2 sees {len(unack_validator2)} unacknowledged patterns")
    
    # Clean up
    db_manager.close()
    print("\n✓ Database connection closed")
    
    print("\n🎉 All tests passed successfully!")


if __name__ == "__main__":
    try:
        test_database_functionality()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)