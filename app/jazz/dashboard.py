"""Jazz-powered dashboard (no backend needed)."""
import reflex as rx
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class JazzDashboardBridge:
    """Bridge for Jazz-only dashboard operations."""

    @staticmethod
    def get_all_feedback() -> str:
        """Get all feedback from Jazz collection."""
        return """
        (async () => {
            const { AppState, JazzHelpers } = await import('/app/jazz/schema');

            const stateId = localStorage.getItem('jazz_app_state_id');
            if (!stateId) return [];

            const appState = await AppState.load(stateId);
            if (!appState || !appState.allFeedback || !appState.allFeedback.items) {
                return [];
            }

            return Array.from(appState.allFeedback.items).map(
                item => JazzHelpers.feedbackToJSON(item)
            );
        })()
        """

    @staticmethod
    def filter_feedback(from_date: str = "", to_date: str = "", ratings: List[int] = []) -> str:
        """Filter feedback with Jazz helpers."""
        ratings_json = str(ratings) if ratings else "[]"
        return f"""
        (async () => {{
            const {{ AppState, JazzHelpers }} = await import('/app/jazz/schema');

            const stateId = localStorage.getItem('jazz_app_state_id');
            if (!stateId) return [];

            const appState = await AppState.load(stateId);
            if (!appState || !appState.allFeedback || !appState.allFeedback.items) {{
                return [];
            }}

            let items = Array.from(appState.allFeedback.items);

            // Filter by date range
            items = JazzHelpers.filterByDateRange(
                items,
                '{from_date}' || undefined,
                '{to_date}' || undefined
            );

            // Filter by ratings
            items = JazzHelpers.filterByRatings(items, {ratings_json});

            return items.map(item => JazzHelpers.feedbackToJSON(item));
        }})()
        """

    @staticmethod
    def get_couriers() -> str:
        """Get all couriers from Jazz."""
        return """
        (async () => {
            const { AppState, JazzHelpers } = await import('/app/jazz/schema');

            const stateId = localStorage.getItem('jazz_app_state_id');
            if (!stateId) return [];

            const appState = await AppState.load(stateId);
            if (!appState || !appState.couriers || !appState.couriers.items) {
                return [];
            }

            return Array.from(appState.couriers.items).map(
                courier => JazzHelpers.courierToJSON(courier)
            );
        })()
        """

    @staticmethod
    def authenticate_admin(username: str, password_hash: str) -> str:
        """Authenticate admin against Jazz store."""
        return f"""
        (async () => {{
            const {{ AppState }} = await import('/app/jazz/schema');

            const stateId = localStorage.getItem('jazz_app_state_id');
            if (!stateId) return false;

            const appState = await AppState.load(stateId);
            if (!appState || !appState.admins || !appState.admins.users) {{
                return false;
            }}

            const admin = Array.from(appState.admins.users).find(
                user => user.username === '{username}' &&
                        user.passwordHash === '{password_hash}'
            );

            if (admin) {{
                admin.lastLogin = new Date().toISOString();
                return true;
            }}

            return false;
        }})()
        """

    @staticmethod
    def export_feedback_csv() -> str:
        """Export feedback as CSV from Jazz."""
        return """
        (async () => {
            const { AppState, JazzHelpers } = await import('/app/jazz/schema');

            const stateId = localStorage.getItem('jazz_app_state_id');
            if (!stateId) return '';

            const appState = await AppState.load(stateId);
            if (!appState || !appState.allFeedback || !appState.allFeedback.items) {
                return '';
            }

            const items = Array.from(appState.allFeedback.items).map(
                item => JazzHelpers.feedbackToJSON(item)
            );

            // Build CSV
            const headers = ['Order ID', 'Courier ID', 'Rating', 'Comment', 'Reasons', 'Consent', 'Follow-up', 'Created'];
            const rows = items.map(item => [
                item.order_id,
                item.courier_id,
                item.rating,
                item.comment,
                JSON.stringify(item.reasons),
                item.publish_consent,
                item.needs_follow_up,
                item.created_at
            ]);

            let csv = headers.join(',') + '\\n';
            csv += rows.map(row => row.map(cell => `"${cell}"`).join(',')).join('\\n');

            return csv;
        })()
        """

    @staticmethod
    def seed_default_data() -> str:
        """Seed Jazz with default admin and courier."""
        return """
        (async () => {
            const { AppState, Courier, AdminUser, JazzHelpers } = await import('/app/jazz/schema');

            const stateId = localStorage.getItem('jazz_app_state_id');
            if (!stateId) {
                console.error('No app state found');
                return false;
            }

            const appState = await AppState.load(stateId);
            if (!appState) return false;

            // Seed default admin (username: admin, password: admin)
            // bcrypt hash of "admin": $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqxT5ZqJGi
            if (appState.admins && appState.admins.users && appState.admins.users.length === 0) {
                const admin = AdminUser.create(
                    JazzHelpers.createAdminUser(
                        'admin',
                        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqxT5ZqJGi'
                    ),
                    { owner: appState._owner }
                );
                appState.admins.users.push(admin);
            }

            // Seed sample courier
            if (appState.couriers && appState.couriers.items && appState.couriers.items.length === 0) {
                const courier = Courier.create(
                    JazzHelpers.createCourier({
                        id: 123,
                        name: 'Alex Doe',
                        phone: '+1-800-555-0101',
                        contactLink: 'https://t.me/alex_courier'
                    }),
                    { owner: appState._owner }
                );
                appState.couriers.items.push(courier);
            }

            return true;
        })()
        """
