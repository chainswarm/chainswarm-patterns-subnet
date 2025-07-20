# Database Setup for ChainSwarm Patterns Subnet

This directory contains Docker Compose configurations for PostgreSQL databases used by miners and validators.

## Overview

- **Miner Database**: Runs on port `5433` with pgAdmin on port `8081`
- **Validator Database**: Runs on port `5434` with pgAdmin on port `8082`

## Quick Start

### For Miners

1. Navigate to the miner directory:
   ```bash
   cd ops/miner
   ```

2. Start the PostgreSQL and pgAdmin services:
   ```bash
   docker-compose up -d
   ```

3. Access pgAdmin at `http://localhost:8081`
   - Email: `admin@chainswarm.com`
   - Password: `admin_password`

### For Validators

1. Navigate to the validator directory:
   ```bash
   cd ops/validator
   ```

2. Start the PostgreSQL and pgAdmin services:
   ```bash
   docker-compose up -d
   ```

3. Access pgAdmin at `http://localhost:8082`
   - Email: `admin@chainswarm-validator.com`
   - Password: `admin_password`

## Database Configuration

### Miner Database
- **Host**: localhost
- **Port**: 5433
- **Database**: chainswarm_miner
- **Username**: miner_user
- **Password**: miner_password

### Validator Database
- **Host**: localhost
- **Port**: 5434
- **Database**: chainswarm_validator
- **Username**: validator_user
- **Password**: validator_password

## Environment Variables

You can override the default database settings using environment variables:

### For Miners:
```bash
export MINER_DB_HOST=localhost
export MINER_DB_PORT=5433
export MINER_DB_NAME=chainswarm_miner
export MINER_DB_USER=miner_user
export MINER_DB_PASSWORD=miner_password
```

### For Validators:
```bash
export VALIDATOR_DB_HOST=localhost
export VALIDATOR_DB_PORT=5434
export VALIDATOR_DB_NAME=chainswarm_validator
export VALIDATOR_DB_USER=validator_user
export VALIDATOR_DB_PASSWORD=validator_password
```

## Using the Database in Code

### For Miners:
```python
from core.miner.database import DataManager

# Create a miner database manager
db_manager = DataManager(role="miner")

# Add a pattern
pattern = db_manager.add_pattern(
    pattern_id="example_pattern",
    network="ethereum",
    asset_symbol="ETH",
    data='{"price": 2000, "volume": 1000000}',
    importance=5
)

# Get unacknowledged patterns for a validator
unacknowledged = db_manager.get_unacknowledged_patterns("validator_hotkey_123")
```

### For Validators:
```python
from core.miner.database import DataManager

# Create a validator database manager
db_manager = DataManager(role="validator")

# Acknowledge a pattern
success = db_manager.acknowledge_pattern(pattern_id=1, validator_hotkey="validator_hotkey_123")
```

## Stopping Services

To stop the database services:

```bash
# For miners
cd ops/miner
docker-compose down

# For validators
cd ops/validator
docker-compose down
```

To stop and remove all data:

```bash
# For miners
cd ops/miner
docker-compose down -v

# For validators
cd ops/validator
docker-compose down -v
```

## Troubleshooting

### Connection Issues

1. Ensure Docker is running
2. Check if ports 5433/5434 are available
3. Verify environment variables are set correctly
4. Check Docker logs: `docker-compose logs`

### Database Schema

The database automatically creates the following tables:
- `patterns`: Stores pattern data
- `acknowledged_patterns`: Tracks validator acknowledgments

### pgAdmin Setup

When first accessing pgAdmin:

1. Click "Add New Server"
2. General tab: Name = "ChainSwarm DB"
3. Connection tab:
   - Host: `postgres-miner` (for miner) or `postgres-validator` (for validator)
   - Port: `5432` (internal Docker port)
   - Database: `chainswarm_miner` or `chainswarm_validator`
   - Username: `miner_user` or `validator_user`
   - Password: `miner_password` or `validator_password`

## Security Notes

- Change default passwords in production
- Use environment variables for sensitive configuration
- Consider using Docker secrets for production deployments
- Restrict network access to database ports in production