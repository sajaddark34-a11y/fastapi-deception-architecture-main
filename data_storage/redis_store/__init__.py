"""
Redis Storage Subpackage (`data_storage.redis_store`).

Exposes asynchronous session state management (`SessionStateStore`) and real-time
alert/telemetry streaming (`FastAlertsStream`) along with pre-instantiated singletons.
"""

from data_storage.redis_store.fast_alerts_stream import FastAlertsStream
from data_storage.redis_store.session_state_store import SessionStateStore

session_state_store = SessionStateStore()
fast_alerts_stream = FastAlertsStream()

__all__ = [
    "SessionStateStore",
    "FastAlertsStream",
    "session_state_store",
    "fast_alerts_stream",
]
