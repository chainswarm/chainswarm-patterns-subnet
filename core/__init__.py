# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# TODO(developer): Set your name
# Copyright © 2023 <your name>

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.


# Define the version of the template module.
__version__ = "0.1.0"
version_split = __version__.split(".")
__spec_version__ = (
    (1000 * int(version_split[0]))
    + (10 * int(version_split[1]))
    + (1 * int(version_split[2]))
)

# Import all submodules.
from . import protocol
from . import base
from . import validator
from .subnet_links import SUBNET_LINKS

import os

def get_database_url(role: str = "miner") -> str:
    if role == "miner":
        host = os.getenv("MINER_DB_HOST", "localhost")
        port = os.getenv("MINER_DB_PORT", "5433")
        database = os.getenv("MINER_DB_NAME", "chainswarm_miner")
        username = os.getenv("MINER_DB_USER", "miner_user")
        password = os.getenv("MINER_DB_PASSWORD", "miner_password")
    else:
        host = os.getenv("VALIDATOR_DB_HOST", "localhost")
        port = os.getenv("VALIDATOR_DB_PORT", "5434")
        database = os.getenv("VALIDATOR_DB_NAME", "chainswarm_validator")
        username = os.getenv("VALIDATOR_DB_USER", "validator_user")
        password = os.getenv("VALIDATOR_DB_PASSWORD", "validator_password")

    return f"postgresql://{username}:{password}@{host}:{port}/{database}"