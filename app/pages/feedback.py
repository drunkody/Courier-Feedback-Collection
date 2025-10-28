"""User-facing feedback page."""
import reflex as rx
from app.states.feedback_state import FeedbackState

REASON_OPTIONS = ["Punctuality", "Politeness", "Item Condition", "Packaging", "Other"]


def toast_notification() -> rx.Component:
    """Toast notification component."""
    return rx.cond(
        FeedbackState.show_toast,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    # Icon based on type
                    rx.match(
                        FeedbackState.toast_type,
                        ("success", rx.icon("check_circle", class_name="h-5 w-5 text-green-500")),
                        ("error", rx.icon("x_circle", class_name="h-5 w-5 text-red-500")),
                        ("warning", rx.icon("alert_triangle", class_name="h-5 w-5 text-yellow-500")),
                        ("info", rx.icon("info", class_name="h-5 w-5 text-blue-500")),
                    ),
                    rx.el.p(
                        FeedbackState.toast_message,
                        class_name="ml-3 text-sm font-mono text-gray-700"
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="h-4 w-4"),
                        on_click=FeedbackState.hide_toast,
                        class_name="ml-auto text-gray-400 hover:text-gray-600",
                    ),
                    class_name="flex items-center p-4",
                ),
                class_name=rx.match(
                    FeedbackState.toast_type,
                    ("success", "bg-green-50 border-l-4 border-green-500"),
                    ("error", "bg-red-50 border-l-4 border-red-500"),
                    ("warning", "bg-yellow-50 border-l-4 border-yellow-500"),
                    ("info", "bg-blue-50 border-l-4 border-blue-500"),
                    "bg-gray-50 border-l-4 border-gray-500",
                ),
                style={
                    "animation": "slideIn 0.3s ease-out"
                }
            ),
            class_name="fixed top-4 right-4 z-50 max-w-md shadow-lg rounded-lg",
        )
    )


def online_indicator() -> rx.Component:
    """Show online/offline status."""
    return rx.cond(
        FeedbackState.pending_count > 0,
        rx.el.div(
            rx.icon("cloud_off", class_name="h-4 w-4 mr-2"),
            rx.el.span(
                f"{FeedbackState.pending_count} pending sync",
                class_name="text-xs font-mono"
            ),
            class_name="fixed top-4 left-4 bg-yellow-100 text-yellow-800 px-3 py-2 rounded-full shadow-md flex items-center",
        )
    )


def rating_stars() -> rx.Component:
    """Star rating selector component."""
    return rx.el.div(
        rx.foreach(
            range(1, 6),
            lambda i: rx.el.button(
                rx.icon(
                    "star",
                    fill=rx.cond(FeedbackState.rating >= i, "currentColor", "none"),
                    class_name="h-8 w-8",
                ),
                on_click=lambda: FeedbackState.set_rating(i),
                class_name=rx.cond(
                    FeedbackState.rating >= i,
                    "text-blue-500",
                    "text-gray-300"
                ),
                background="transparent",
                border="none",
                cursor="pointer",
            ),
        ),
        class_name="flex justify-center gap-2",
    )


def reason_checkbox(reason: str) -> rx.Component:
    """Checkbox for feedback reasons."""
    return rx.el.label(
        rx.el.input(
            type="checkbox",
            checked=FeedbackState.reasons.contains(reason),
            on_change=lambda: FeedbackState.toggle_reason(reason),
            class_name="h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer",
        ),
        rx.el.span(reason, class_name="ml-3 text-base text-gray-700 font-mono"),
        class_name="flex items-center",
    )


def feedback_form() -> rx.Component:
    """Main feedback form."""
    return rx.el.div(
        rx.el.h1(
            "Rate Your Delivery",
            class_name="text-2xl font-bold text-gray-800 mb-2 font-mono",
        ),
        rx.el.p(
            f"Order ID: {FeedbackState.order_id}",
            class_name="text-sm text-gray-500 mb-6 font-mono",
        ),

        # Star rating
        rx.el.div(rating_stars(), class_name="mb-6"),

        # Comment textarea
        rx.el.div(
            rx.el.label(
                "Your Comment",
                html_for="comment",
                class_name="block text-sm font-medium text-gray-700 font-mono mb-2",
            ),
            rx.el.textarea(
                id="comment",
                placeholder="How was your experience?",
                on_change=FeedbackState.set_comment,
                max_length=500,
                class_name="w-full p-3 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 transition font-mono",
                default_value=FeedbackState.comment,
            ),
            rx.el.p(
                f"{FeedbackState.comment_length}/500",
                class_name=rx.cond(
                    FeedbackState.comment_length > 500,
                    "text-xs text-red-600 mt-1 text-right font-mono",
                    "text-xs text-gray-500 mt-1 text-right font-mono",
                ),
            ),
            class_name="mb-6",
        ),

        # Reason checkboxes
        rx.el.div(
            rx.el.h3(
                "What went well?",
                class_name="text-lg font-medium text-gray-800 mb-4 font-mono",
            ),
            rx.el.div(
                rx.foreach(REASON_OPTIONS, reason_checkbox),
                class_name="grid grid-cols-2 gap-4",
            ),
            class_name="mb-6",
        ),

        # Publish consent
        rx.el.label(
            rx.el.input(
                type="checkbox",
                checked=FeedbackState.publish_consent,
                on_change=FeedbackState.set_publish_consent,
                class_name="h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer",
            ),
            rx.el.span(
                "I agree to my feedback being published anonymously.",
                class_name="ml-3 text-sm text-gray-600 font-mono",
            ),
            class_name="flex items-center mb-8",
        ),

        # Queue indicator
        rx.cond(
            FeedbackState.pending_count > 0,
            rx.el.p(f"📦 {FeedbackState.pending_count} feedback(s) waiting to sync", class_name="text-xs text-gray-500 mb-4 text-center font-mono"),
        ),

        # Submit button
        rx.el.button(
            "Submit Feedback",
            on_click=FeedbackState.submit_feedback,
            disabled=~FeedbackState.can_submit,
            class_name="w-full bg-blue-600 text-white font-bold py-3 px-4 rounded-lg shadow-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 font-mono",
        ),
        class_name="w-full max-w-md",
    )


def thank_you_screen() -> rx.Component:
    """Thank you confirmation screen."""
    return rx.el.div(
        rx.el.div(
            rx.icon("square_check", class_name="h-16 w-16 text-green-500 mx-auto"),
            class_name="mb-4",
        ),
        rx.el.h1(
            "Thank You!",
            class_name="text-3xl font-bold text-gray-800 mb-2 font-mono text-center",
        ),
        rx.el.p(
            "Your feedback has been submitted.",
            class_name="text-gray-600 mb-8 font-mono text-center",
        ),

        # Courier contact card
        rx.cond(
            FeedbackState.courier,
            rx.el.div(
                rx.el.h2(
                    "Contact Your Courier",
                    class_name="text-xl font-semibold text-gray-700 mb-4 border-b pb-2 font-mono",
                ),
                rx.el.div(
                    rx.el.p(
                        rx.icon("user", class_name="inline-block mr-2 h-5 w-5"),
                        FeedbackState.courier["name"],
                        class_name="text-lg font-mono",
                    ),
                    rx.el.a(
                        rx.icon("phone", class_name="inline-block mr-2 h-5 w-5"),
                        FeedbackState.courier["phone"],
                        href=f"tel:{FeedbackState.courier['phone']}",
                        class_name="text-lg text-blue-600 hover:underline font-mono",
                    ),
                    rx.cond(
                        FeedbackState.courier["contact_link"],
                        rx.el.a(
                            rx.icon("send", class_name="inline-block mr-2 h-5 w-5"),
                            "Contact via Link",
                            href=FeedbackState.courier["contact_link"],
                            target="_blank",
                            class_name="text-lg text-blue-600 hover:underline font-mono",
                        ),
                    ),
                    class_name="space-y-3",
                ),
                class_name="bg-white p-6 rounded-lg border shadow-sm w-full max-w-md",
            ),
        ),
        class_name="flex flex-col items-center w-full max-w-md",
    )


def error_message(icon: str, title: str, message: str) -> rx.Component:
    """Generic error message display."""
    return rx.el.div(
        rx.icon(icon, class_name="h-12 w-12 text-red-500 mx-auto mb-4"),
        rx.el.h1(title, class_name="text-2xl font-bold text-red-500 mb-2 font-mono text-center"),
        rx.el.p(message, class_name="text-gray-600 font-mono text-center"),
        class_name="bg-white p-8 rounded-lg shadow-lg w-full max-w-md",
    )


def queued_message() -> rx.Component:
    """Message for queued submissions."""
    return rx.el.div(
        rx.icon("clock", class_name="h-12 w-12 text-blue-500 mx-auto mb-4"),
        rx.el.h1("Feedback Saved!", class_name="text-2xl font-bold text-blue-600 mb-2 font-mono text-center"),
        rx.el.p("Your feedback is saved locally and will sync automatically when you're back online.", class_name="text-gray-600 font-mono text-center mb-4"),
        rx.el.p(f"📦 {FeedbackState.pending_count} pending sync", class_name="text-sm text-gray-500 font-mono text-center"),
        class_name="bg-white p-8 rounded-lg shadow-lg w-full max-w-md",
    )


@rx.page(route="/", on_load=FeedbackState.on_load)
def feedback_page() -> rx.Component:
    """Main feedback page with state-based rendering."""
    return rx.el.main(
        # Toast notifications
        toast_notification(),

        # Online/offline indicator
        online_indicator(),

        rx.el.div(
            rx.match(
                FeedbackState.submission_status,
                ("idle", feedback_form()),
                ("submitting", rx.spinner(class_name="h-12 w-12 text-blue-600")),
                ("success", thank_you_screen()),
                ("queued", queued_message()),
                ("duplicate", error_message(
                    "badge_alert",
                    "Already Submitted",
                    "Feedback for this order already exists."
                )),
                ("error", error_message(
                    "circle_x",
                    "Error",
                    FeedbackState.error_message
                )),
                rx.spinner(class_name="h-12 w-12 text-blue-600"),
            ),
            class_name="container mx-auto max-w-lg p-6 flex flex-col items-center justify-center min-h-screen",
        ),
        class_name="font-['JetBrains_Mono'] bg-gray-50",
        # Online/offline event listeners
        on_mount=rx.call_script("""
            window.addEventListener('online', () => {
                console.log('Back online');
                window.dispatchEvent(new CustomEvent('reflex:update_online_status', {detail: {is_online: true}}));
            });
            window.addEventListener('offline', () => {
                console.log('Gone offline');
                window.dispatchEvent(new CustomEvent('reflex:update_online_status', {detail: {is_online: false}}));
            });
        """),
    )
