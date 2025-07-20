"""
SQLAlchemy database models and data manager for validator pattern storage.

This module provides:
- Pattern table for storing patterns received from miners with verification results
- ValidatorDataManager class for database operations
"""

import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from sqlalchemy import (
    create_engine, 
    Column, 
    BigInteger, 
    String, 
    Text, 
    DateTime, 
    Integer,
    Boolean,
    Float,
    Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func

Base = declarative_base()


class VerificationStatus(Enum):
    """Enumeration for pattern verification status."""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    INVALID = "invalid"


def get_database_url(role: str = "validator") -> str:
    """
    Get database URL from environment variables or use defaults.
    
    Args:
        role: Either "miner" or "validator" to determine which database to connect to
        
    Returns:
        PostgreSQL database URL
    """
    if role == "miner":
        # Miner database configuration
        host = os.getenv("MINER_DB_HOST", "localhost")
        port = os.getenv("MINER_DB_PORT", "5433")
        database = os.getenv("MINER_DB_NAME", "chainswarm_miner")
        username = os.getenv("MINER_DB_USER", "miner_user")
        password = os.getenv("MINER_DB_PASSWORD", "miner_password")
    else:
        # Validator database configuration
        host = os.getenv("VALIDATOR_DB_HOST", "localhost")
        port = os.getenv("VALIDATOR_DB_PORT", "5434")
        database = os.getenv("VALIDATOR_DB_NAME", "chainswarm_validator")
        username = os.getenv("VALIDATOR_DB_USER", "validator_user")
        password = os.getenv("VALIDATOR_DB_PASSWORD", "validator_password")
    
    return f"postgresql://{username}:{password}@{host}:{port}/{database}"


class Pattern(Base):
    """
    Pattern table for storing patterns received from miners with verification results.
    
    Columns:
    - id: Big integer auto increment primary key
    - pattern_id: String max length for pattern identifier
    - network: String for network name
    - asset_symbol: String for asset symbol
    - asset_contract: String for asset contract (native by default)
    - data: Text field for pattern data (nullable)
    - timestamp: DateTime for when pattern was received
    - miner_hotkey: String for the miner's hotkey who submitted the pattern
    - verification_status: Enum for verification result (pending, verified, rejected, invalid)
    - verification_score: Float for verification score (0.0 to 1.0)
    - verification_timestamp: DateTime for when verification was completed
    - verification_details: Text field for additional verification information
    """
    __tablename__ = 'patterns'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    pattern_id = Column(String(255), nullable=False, index=True)
    network = Column(String(100), nullable=False)
    asset_symbol = Column(String(50), nullable=False)
    asset_contract = Column(String(255), nullable=False, default='native')
    data = Column(Text, nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Miner information
    miner_hotkey = Column(String(255), nullable=False, index=True)
    
    # Verification results
    verification_status = Column(SQLEnum(VerificationStatus), nullable=False, default=VerificationStatus.PENDING, index=True)
    verification_score = Column(Float, nullable=True)  # 0.0 to 1.0
    verification_timestamp = Column(DateTime, nullable=True)
    verification_details = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Pattern(id={self.id}, pattern_id='{self.pattern_id}', miner='{self.miner_hotkey}', status='{self.verification_status.value}')>"


class ValidatorDataManager:
    """
    Data manager class for handling validator database operations.
    
    Provides methods to:
    - Store patterns received from miners
    - Update verification results
    - Query patterns by various criteria
    - Manage database sessions and connections
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize the ValidatorDataManager with database connection.
        
        Args:
            database_url: SQLAlchemy database URL. If None, uses PostgreSQL with default validator configuration.
        """
        if database_url is None:
            database_url = get_database_url("validator")
        
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
    
    def store_pattern(
        self,
        pattern_id: str,
        network: str,
        asset_symbol: str,
        miner_hotkey: str,
        data: Optional[str] = None,
        asset_contract: str = 'native'
    ) -> Optional[Pattern]:
        """
        Store a pattern received from a miner.
        
        Args:
            pattern_id: Unique identifier for the pattern
            network: Network name
            asset_symbol: Asset symbol
            miner_hotkey: Hotkey of the miner who submitted the pattern
            data: Pattern data (optional)
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
                miner_hotkey=miner_hotkey,
                timestamp=datetime.utcnow(),
                verification_status=VerificationStatus.PENDING
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
    
    def update_verification_result(
        self,
        pattern_id: int,
        status: VerificationStatus,
        score: Optional[float] = None,
        details: Optional[str] = None
    ) -> bool:
        """
        Update the verification result for a pattern.
        
        Args:
            pattern_id: The database ID of the pattern
            status: Verification status
            score: Verification score (0.0 to 1.0, optional)
            details: Additional verification details (optional)
            
        Returns:
            True if update was successful, False otherwise
        """
        session = self.get_session()
        try:
            pattern = session.query(Pattern).filter(Pattern.id == pattern_id).first()
            if not pattern:
                return False
            
            pattern.verification_status = status
            pattern.verification_timestamp = datetime.utcnow()
            
            if score is not None:
                pattern.verification_score = max(0.0, min(1.0, score))  # Clamp between 0.0 and 1.0
            
            if details is not None:
                pattern.verification_details = details
            
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_patterns_by_status(
        self,
        status: VerificationStatus,
        limit: Optional[int] = None,
        miner_hotkey: Optional[str] = None
    ) -> List[Pattern]:
        """
        Get patterns by verification status.
        
        Args:
            status: Verification status to filter by
            limit: Maximum number of patterns to return (optional)
            miner_hotkey: Filter by specific miner hotkey (optional)
            
        Returns:
            List of Pattern objects
        """
        session = self.get_session()
        try:
            query = session.query(Pattern).filter(Pattern.verification_status == status)
            
            if miner_hotkey:
                query = query.filter(Pattern.miner_hotkey == miner_hotkey)
            
            query = query.order_by(Pattern.timestamp.desc())
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
            
        finally:
            session.close()
    
    def get_pending_patterns(self, limit: Optional[int] = None) -> List[Pattern]:
        """
        Get patterns that are pending verification.
        
        Args:
            limit: Maximum number of patterns to return (optional)
            
        Returns:
            List of pending Pattern objects
        """
        return self.get_patterns_by_status(VerificationStatus.PENDING, limit)
    
    def get_verified_patterns(self, limit: Optional[int] = None) -> List[Pattern]:
        """
        Get patterns that have been verified.
        
        Args:
            limit: Maximum number of patterns to return (optional)
            
        Returns:
            List of verified Pattern objects
        """
        return self.get_patterns_by_status(VerificationStatus.VERIFIED, limit)
    
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
    
    def get_patterns_by_miner(
        self,
        miner_hotkey: str,
        status: Optional[VerificationStatus] = None,
        limit: Optional[int] = None
    ) -> List[Pattern]:
        """
        Get patterns submitted by a specific miner.
        
        Args:
            miner_hotkey: The miner's hotkey
            status: Filter by verification status (optional)
            limit: Maximum number of patterns to return (optional)
            
        Returns:
            List of Pattern objects
        """
        session = self.get_session()
        try:
            query = session.query(Pattern).filter(Pattern.miner_hotkey == miner_hotkey)
            
            if status:
                query = query.filter(Pattern.verification_status == status)
            
            query = query.order_by(Pattern.timestamp.desc())
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
            
        finally:
            session.close()
    
    def get_verification_statistics(self) -> Dict[str, Any]:
        """
        Get verification statistics.
        
        Returns:
            Dictionary with verification statistics
        """
        session = self.get_session()
        try:
            total_patterns = session.query(Pattern).count()
            pending_count = session.query(Pattern).filter(Pattern.verification_status == VerificationStatus.PENDING).count()
            verified_count = session.query(Pattern).filter(Pattern.verification_status == VerificationStatus.VERIFIED).count()
            rejected_count = session.query(Pattern).filter(Pattern.verification_status == VerificationStatus.REJECTED).count()
            invalid_count = session.query(Pattern).filter(Pattern.verification_status == VerificationStatus.INVALID).count()
            
            avg_score = session.query(func.avg(Pattern.verification_score)).filter(
                Pattern.verification_score.isnot(None)
            ).scalar()
            
            return {
                "total_patterns": total_patterns,
                "pending": pending_count,
                "verified": verified_count,
                "rejected": rejected_count,
                "invalid": invalid_count,
                "average_verification_score": float(avg_score) if avg_score else 0.0
            }
            
        finally:
            session.close()
    
    def close(self):
        """Close the database engine."""
        self.engine.dispose()


# Convenience function to create a ValidatorDataManager instance
def create_validator_data_manager(database_url: Optional[str] = None) -> ValidatorDataManager:
    """
    Create a ValidatorDataManager instance.
    
    Args:
        database_url: SQLAlchemy database URL. If None, uses PostgreSQL with default validator configuration.
        
    Returns:
        ValidatorDataManager instance
    """
    return ValidatorDataManager(database_url)