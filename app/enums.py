from enum import Enum


class AppMode(Enum):
    """Application deployment modes."""
    TRADITIONAL = "traditional"  # Backend only, no Jazz
    JAZZ_ONLY = "jazz_only"      # Jazz only, no backend
    HYBRID = "hybrid"             # Both Jazz and Backend
    OFFLINE_FIRST = "offline_first"  # Jazz primary, backend fallback
