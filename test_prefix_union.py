import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent / "src"))

from data_prep import prefix_union_address_count


def test_prefix_union():
    prefixes = ["10.0.0.0/16", "10.0.1.0/24"]
    assert prefix_union_address_count(prefixes) == 65536