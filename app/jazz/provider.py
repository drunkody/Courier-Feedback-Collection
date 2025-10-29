"""Jazz provider component for Reflex."""
import reflex as rx
from typing import Optional

class JazzProvider(rx.Component):
    """
    Jazz sync provider component.
    Wraps the application with Jazz real-time sync capabilities.
    """
    library = "jazz-react"
    tag = "JazzProvider"

    # Props
    auth: rx.Var[str] = "anonymous"  # Auth strategy
    sync_server: rx.Var[str] = ""
    enable_p2p: rx.Var[bool] = True
    storage: rx.Var[str] = "indexedDB"  # Storage backend

    def get_event_triggers(self) -> dict:
        """Define event triggers for Jazz."""
        return {
            "on_sync": lambda: [],
            "on_error": lambda error: [error],
        }

class UseCoState(rx.Component):
    """
    Hook component to use Jazz CoState.
    Provides reactive access to CRDT data.
    """
    library = "jazz-react"
    tag = "useCoState"
    is_default = True

    # Props
    schema: rx.Var[str]
    id: rx.Var[str]

class JazzLocalProvider(rx.Component):
    """
    Local-only Jazz provider for development/testing.
    No network sync, only local IndexedDB.
    """
    library = "jazz-react"
    tag = "JazzLocalProvider"
    storage: rx.Var[str] = "indexedDB"

def jazz_provider(
    *children,
    sync_server: str = "",
    auth: str = "anonymous",
    enable_p2p: bool = True,
) -> rx.Component:
    """
    Create Jazz provider wrapper.

    Args:
        children: Child components
        sync_server: WebSocket URL for sync server
        auth: Authentication provider (anonymous, clerk, custom)
        enable_p2p: Enable peer-to-peer sync

    Returns:
        JazzProvider component
    """
    return JazzProvider.create(
        *children,
        sync_server=sync_server,
        auth=auth,
        enable_p2p=enable_p2p,
    )
