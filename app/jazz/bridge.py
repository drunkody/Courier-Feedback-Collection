"""Bridge between Jazz (JavaScript) and Reflex (Python) state."""
import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class JazzBridge:
    """
    Bridge for communicating with Jazz from Python.

    NOTE: This is a template/placeholder implementation.
    Actual JS execution requires custom Reflex integration or script tags.
    """

    @staticmethod
    def init_queue(queue_id: str) -> str:
        """
        Initialize Jazz queue.
        Returns JavaScript code to execute.
        """
        return f"""
        (async () => {{
            const {{ PendingFeedbackQueue, AppState }} = await import('/app/jazz/schema.js');
            const {{ useAccount }} = await import('jazz-react');

            // Get current account/user
            const account = useAccount();
            if (!account) {{
                console.error('No Jazz account available');
                return null;
            }}

            let queue = await PendingFeedbackQueue.load('{queue_id}');
            if (!queue) {{
                queue = PendingFeedbackQueue.create([], {{ owner: account }});
                localStorage.setItem('jazz_queue_id', queue.id);
            }}
            return queue.id;
        }})()
        """

    @staticmethod
    def add_to_queue(feedback_data: Dict[str, Any]) -> str:
        """
        Add feedback to Jazz queue.
        Returns JavaScript code to execute.
        """
        data_json = json.dumps(feedback_data)
        return f"""
        (async () => {{
            const {{ FeedbackItem, PendingFeedbackQueue, JazzHelpers }} = await import('/app/jazz/schema.js');
            const {{ useAccount }} = await import('jazz-react');

            const account = useAccount();
            if (!account) return false;

            const queueId = localStorage.getItem('jazz_queue_id');
            const queue = await PendingFeedbackQueue.load(queueId);
            if (queue) {{
                const feedbackData = {data_json};
                const itemData = JazzHelpers.createFeedbackItem(feedbackData);
                const item = FeedbackItem.create(itemData, {{ owner: queue._owner }});
                queue.push(item);
                return true;
            }}
            return false;
        }})()
        """

    @staticmethod
    def get_queue_items() -> str:
        """
        Get all items from Jazz queue.
        Returns JavaScript code to execute.
        """
        return """
        (async () => {
            const { PendingFeedbackQueue, JazzHelpers } = await import('/app/jazz/schema.js');
            const queueId = localStorage.getItem('jazz_queue_id');
            if (!queueId) return [];
            const queue = await PendingFeedbackQueue.load(queueId);
            if (!queue) return [];
            return Array.from(queue).map(item => JazzHelpers.feedbackToJSON(item));
        })()
        """

    @staticmethod
    def remove_from_queue(order_id: str) -> str:
        """
        Remove item from Jazz queue by order_id.
        Returns JavaScript code to execute.
        """
        return f"""
        (async () => {{
            const {{ PendingFeedbackQueue }} = await import('/app/jazz/schema.js');
            const queueId = localStorage.getItem('jazz_queue_id');
            const queue = await PendingFeedbackQueue.load(queueId);
            if (queue) {{
                const index = Array.from(queue).findIndex(
                    item => item.orderId === '{order_id}'
                );
                if (index !== -1) {{
                    queue.splice(index, 1);
                    return true;
                }}
            }}
            return false;
        }})()
        """

    @staticmethod
    def mark_as_synced(order_id: str) -> str:
        """
        Mark item as synced in Jazz queue.
        Returns JavaScript code to execute.
        """
        return f"""
        (async () => {{
            const {{ PendingFeedbackQueue, JazzHelpers }} = await import('/app/jazz/schema.js');
            const queueId = localStorage.getItem('jazz_queue_id');
            const queue = await PendingFeedbackQueue.load(queueId);
            if (queue) {{
                const item = Array.from(queue).find(
                    item => item.orderId === '{order_id}'
                );
                if (item) {{
                    JazzHelpers.markAsSynced(item);
                    return true;
                }}
            }}
            return false;
        }})()
        """

    @staticmethod
    def get_queue_count() -> str:
        """
        Get count of pending items.
        Returns JavaScript code to execute.
        """
        return """
        (async () => {
            const { PendingFeedbackQueue } = await import('/app/jazz/schema.js');
            const queueId = localStorage.getItem('jazz_queue_id');
            if (!queueId) return 0;
            const queue = await PendingFeedbackQueue.load(queueId);
            return queue ? queue.length : 0;
        })()
        """

    @staticmethod
    def clear_synced_items() -> str:
        """
        Remove all synced items from queue.
        Returns JavaScript code to execute.
        """
        return """
        (async () => {
            const { PendingFeedbackQueue } = await import('/app/jazz/schema.js');
            const queueId = localStorage.getItem('jazz_queue_id');
            const queue = await PendingFeedbackQueue.load(queueId);
            if (queue) {
                let removed = 0;
                for (let i = queue.length - 1; i >= 0; i--) {
                    if (queue[i].synced) {
                        queue.splice(i, 1);
                        removed++;
                    }
                }
                return removed;
            }
            return 0;
        })()
        """


# FIXED: Removed JazzStateManager - it relied on non-existent call_script method
# Jazz integration would need to be implemented differently in Reflex
