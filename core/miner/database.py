"""
SQLAlchemy database models and data manager for storing patterns.

This module provides:
- Patterns table for storing pattern data
- AcknowledgedPatterns table for tracking validator acknowledgments
- DataManager class for database operations
"""

import os
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    create_engine,
    Column,
    BigInteger,
    String,
    Text,
    DateTime,
    Integer,
    ForeignKey,
    and_,
    or_
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship

from core import get_database_url

Base = declarative_base()

class Pattern(Base):
    __tablename__ = 'patterns'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    pattern_id = Column(String(255), nullable=False, index=True)
    network = Column(String(100), nullable=False)
    asset_symbol = Column(String(50), nullable=False)
    asset_contract = Column(String(255), nullable=False, default='native')
    data = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    importance = Column(Integer, nullable=False, default=0)
    
    # Relationship to acknowledged patterns
    acknowledgments = relationship("AcknowledgedPattern", back_populates="pattern")
    
    def __repr__(self):
        return f"<Pattern(id={self.id}, pattern_id='{self.pattern_id}', network='{self.network}', importance={self.importance})>"


class AcknowledgedPattern(Base):

    __tablename__ = 'acknowledged_patterns'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    pattern_id = Column(BigInteger, ForeignKey('patterns.id'), nullable=False, index=True)
    validator_hotkey = Column(String(255), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationship to pattern
    pattern = relationship("Pattern", back_populates="acknowledgments")
    
    def __repr__(self):
        return f"<AcknowledgedPattern(id={self.id}, pattern_id={self.pattern_id}, validator_hotkey='{self.validator_hotkey}')>"


class DataManager:

    def __init__(self, database_url: str):
        """
        Initialize the DataManager with database connection.
        
        Args:
            database_url: SQLAlchemy database URL. If None, uses PostgreSQL with default configuration.
        """

        self.engine = create_engine(
            database_url,
            echo=False,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()
    
    def get_unacknowledged_patterns(
        self, 
        validator_hotkey: str
    ) -> Pattern:

        with self.get_session() as session:
            # Subquery to get pattern IDs that have been acknowledged by this validator
            acknowledged_subquery = session.query(AcknowledgedPattern.pattern_id).filter(
                AcknowledgedPattern.validator_hotkey == validator_hotkey
            ).subquery()

            # Main query for unacknowledged patterns
            query = session.query(Pattern).filter(
                ~Pattern.id.in_(acknowledged_subquery)
            )
            query = query.order_by(Pattern.id.asc(), Pattern.importance.desc())
            query = query.limit(1)

            return query.single()

    def acknowledge_pattern(self, pattern_id: int, validator_hotkey: str) -> bool:

        with self.get_session() as session:
            pattern = session.query(Pattern).filter(Pattern.id == pattern_id).first()
            if not pattern:
                return False
            
            # Check if already acknowledged by this validator
            existing_ack = session.query(AcknowledgedPattern).filter(
                and_(
                    AcknowledgedPattern.pattern_id == pattern_id,
                    AcknowledgedPattern.validator_hotkey == validator_hotkey
                )
            ).first()
            
            if existing_ack:
                # Already acknowledged
                return True
            
            # Create new acknowledgment
            acknowledgment = AcknowledgedPattern(
                pattern_id=pattern_id,
                validator_hotkey=validator_hotkey,
                timestamp=datetime.utcnow()
            )
            
            session.add(acknowledgment)
            session.commit()
            return True

    def add_pattern(
        self,
        pattern_id: str,
        network: str,
        asset_symbol: str,
        data: str,
        importance: int = 0,
        asset_contract: str = 'native'
    ) -> Optional[Pattern]:
        """
        Add a new pattern to the database.
        
        Args:
            pattern_id: Unique identifier for the pattern
            network: Network name
            asset_symbol: Asset symbol
            data: Pattern data
            importance: Importance level (default: 0)
            asset_contract: Asset contract address (default: 'native')
            
        Returns:
            The created Pattern object, or None if creation failed
        """
        session = self.get_session()
        try:
            pattern = Pattern(
                pattern_id=pattern_id,
                network=network,
                asset_symbol=asset_symbol,
                asset_contract=asset_contract,
                data=data,
                importance=importance,
                timestamp=datetime.utcnow()
            )
            
            session.add(pattern)
            session.commit()
            session.refresh(pattern)
            return pattern
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_pattern_by_id(self, pattern_id: int) -> Optional[Pattern]:
        """
        Get a pattern by its database ID.
        
        Args:
            pattern_id: The database ID of the pattern
            
        Returns:
            Pattern object if found, None otherwise
        """
        session = self.get_session()
        try:
            return session.query(Pattern).filter(Pattern.id == pattern_id).first()
        finally:
            session.close()
    
    def get_acknowledgment_count(self, pattern_id: int) -> int:
        """
        Get the number of acknowledgments for a specific pattern.
        
        Args:
            pattern_id: The database ID of the pattern
            
        Returns:
            Number of acknowledgments
        """
        session = self.get_session()
        try:
            return session.query(AcknowledgedPattern).filter(
                AcknowledgedPattern.pattern_id == pattern_id
            ).count()
        finally:
            session.close()
    
    def close(self):
        """Close the database engine."""
        self.engine.dispose()


# Convenience function to create a DataManager instance
def create_data_manager(database_url: Optional[str] = None, role: str = "miner") -> DataManager:
    """
    Create a DataManager instance.
    
    Args:
        database_url: SQLAlchemy database URL. If None, uses PostgreSQL with default configuration.
        role: Either "miner" or "validator" to determine which database to connect to
        
    Returns:
        DataManager instance
    """
    return DataManager(database_url, role)