from typing import Callable
from context import Context

Predicate = Callable[[Context], bool]
"""
Alias for a boolean check on pipeline context
"""