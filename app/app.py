"""Main Reflex application."""
import os
import reflex as rx
from fastapi import FastAPI
from config import config
from app.database import create_db_and_tables
from app.api_routes import router

# Setup FastAPI
api = FastAPI()


@api.on_event("startup")
def on_startup():
    """Initialize database on startup."""
    # Only init DB if not in test mode
    if os.getenv("APP_ENV") != "testing":
        create_db_and_tables()


# Include API routes
api.include_router(router)

# Only create Reflex app if not in testing mode
if os.getenv("APP_ENV") != "testing":
    from app.pages.feedback import feedback_page
    from app.pages.login import login_page
    from app.pages.admin_dashboard import dashboard_page
    from app.jazz import jazz_provider

    # Create Reflex app
    app = rx.App(
        theme=rx.theme(appearance="light"),
        head_components=[
            rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
            rx.el.link(
                rel="preconnect",
                href="https://fonts.gstatic.com",
                crossorigin=""
            ),
            rx.el.link(
                href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap",
                rel="stylesheet",
            ),
            # Add toast animation styles
            rx.el.style("""
                @keyframes slideIn {
                    from {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }

                /* Jazz sync indicator animations */
                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.5; }
                }
                .jazz-syncing {
                    animation: pulse 1.5s ease-in-out infinite;
                }
            """),
        ]
        + (
            [
                rx.script(src="https://unpkg.com/jazz-tools@latest/dist/index.js"),
            ]
            if config.USE_JAZZ_SYNC
            else []
        ),
        api_transformer=api,
    )

    # Add pages
    if config.USE_JAZZ_SYNC:
        app.add_page(
            lambda: jazz_provider(feedback_page()),
            route="/",
            title="Delivery Feedback"
        )
    else:
        app.add_page(feedback_page, route="/", title="Delivery Feedback")

    app.add_page(login_page, route="/admin", title="Admin Login")
    app.add_page(dashboard_page, route="/admin/dashboard", title="Admin Dashboard")

