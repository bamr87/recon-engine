"""The Recon Engine core library: an operational event stream reconciled against the general ledger.

Build step 1 of SPEC.md § 6 is in place: the neutral schemas (`OperationalEvent`,
`GLPosting`) and the single monthly number (`monthly_residual`, which returns a
`Residual`). Step 2, the six-bucket decomposition, is next. Standard library only.
"""

from .residual import MissingDirectionError, MissingStandardCostError, Residual, monthly_residual
from .schemas import EventType, GLPosting, JournalType, OperationalEvent

__all__ = [
    "EventType",
    "GLPosting",
    "JournalType",
    "MissingDirectionError",
    "MissingStandardCostError",
    "OperationalEvent",
    "Residual",
    "monthly_residual",
]

__version__ = "0.1.0"
