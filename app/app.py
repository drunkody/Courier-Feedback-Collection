import reflex as rx
from .states.feedback_state import FeedbackState
from .states.admin_state import AdminState
from .pages.login import login_page
from .components.admin_dashboard import dashboard_page
from .database import Courier
from . import api_routes
from fastapi import HTTPException

REASON_OPTIONS = ["Punctuality", "Politeness", "Item Condition", "Packaging", "Other"]


def rating_stars() -> rx.Component:
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
                    FeedbackState.rating >= i, "text-blue-500", "text-gray-300"
                ),
                background="transparent",
                border="none",
                cursor="pointer",
            ),
        ),
        class_name="flex justify-center gap-2",
    )


def reason_checkbox(reason: str) -> rx.Component:
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
    return rx.el.div(
        rx.el.h1(
            "Rate Your Delivery",
            class_name="text-2xl font-bold text-gray-800 mb-2 font-mono",
        ),
        rx.el.p(
            f"Order ID: {FeedbackState.order_id}",
            class_name="text-sm text-gray-500 mb-6 font-mono",
        ),
        rx.el.div(rating_stars(), class_name="mb-6"),
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
        rx.el.button(
            "Submit Feedback",
            on_click=FeedbackState.submit_feedback,
            is_loading=FeedbackState.submission_status == "submitting",
            disabled=~FeedbackState.is_form_valid
            | (FeedbackState.submission_status == "submitting"),
            class_name="w-full bg-blue-600 text-white font-bold py-3 px-4 rounded-lg shadow-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 font-mono",
            style={"box-shadow": "0 4px 6px rgba(0, 0, 0, 0.1)"},
        ),
        class_name="w-full max-w-md",
    )


def thank_you_screen() -> rx.Component:
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
        rx.cond(
            FeedbackState.courier,
            rx.el.div(
                rx.el.h2(
                    "Contact Your Courier",
                    class_name="text-xl font-semibold text-gray-700 mb-4 border-b pb-2 font-mono",
                ),
                rx.el.div(
                    rx.el.p(
                        rx.icon(
                            "user",
                            class_name="inline-block mr-2 h-5 w-5 align-text-bottom text-gray-500",
                        ),
                        FeedbackState.courier["name"],
                        class_name="text-lg font-mono",
                    ),
                    rx.el.a(
                        rx.icon(
                            "phone",
                            class_name="inline-block mr-2 h-5 w-5 align-text-bottom text-gray-500",
                        ),
                        FeedbackState.courier["phone"],
                        href=f"tel:{FeedbackState.courier['phone']}",
                        class_name="text-lg text-blue-600 hover:underline font-mono",
                    ),
                    rx.cond(
                        FeedbackState.courier["contact_link"],
                        rx.el.a(
                            rx.icon(
                                "send",
                                class_name="inline-block mr-2 h-5 w-5 align-text-bottom text-gray-500",
                            ),
                            "Contact via Link",
                            href=FeedbackState.courier["contact_link"],
                            target="_blank",
                            class_name="text-lg text-blue-600 hover:underline font-mono",
                        ),
                    ),
                    class_name="space-y-3",
                ),
                rx.el.p(
                    "You can contact me for future orders.",
                    class_name="mt-6 text-sm text-gray-500 italic font-mono bg-gray-50 p-3 rounded-lg border border-gray-200",
                ),
                class_name="bg-white p-6 rounded-lg border border-gray-200 shadow-sm w-full max-w-md",
            ),
        ),
        class_name="flex flex-col items-center justify-center w-full max-w-md text-left",
    )


def message_card(icon: str, title: str, message: str, color_class: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name=f"h-12 w-12 {color_class} mx-auto"),
            class_name="mb-4",
        ),
        rx.el.h1(
            title,
            class_name=f"text-2xl font-bold {color_class} mb-2 font-mono text-center",
        ),
        rx.el.p(message, class_name="text-gray-600 font-mono text-center"),
        class_name="bg-white p-8 rounded-lg shadow-lg w-full max-w-md",
    )


def loading_spinner() -> rx.Component:
    return rx.el.div(
        rx.spinner(class_name="h-12 w-12 text-blue-600"),
        rx.el.p("Loading...", class_name="mt-4 text-gray-600 font-mono"),
        class_name="flex flex-col items-center justify-center",
    )


@rx.page(route="/", on_load=FeedbackState.on_load)
def index() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            rx.el.button(
                "Seed Courier Data",
                on_click=FeedbackState.seed_data,
                class_name="absolute top-4 right-4 bg-gray-200 text-gray-700 text-xs py-1 px-2 rounded font-mono hover:bg-gray-300",
            ),
            rx.match(
                FeedbackState.submission_status,
                ("idle", feedback_form()),
                ("submitting", loading_spinner()),
                ("success", thank_you_screen()),
                (
                    "duplicate",
                    message_card(
                        "badge_alert",
                        "Already Submitted",
                        "Feedback for this order has already been recorded. Thank you!",
                        "text-yellow-500",
                    ),
                ),
                (
                    "error",
                    message_card(
                        "circle_x",
                        "An Error Occurred",
                        FeedbackState.error_message,
                        "text-red-500",
                    ),
                ),
                loading_spinner(),
            ),
            class_name="container mx-auto max-w-lg p-4 sm:p-6 flex flex-col items-center justify-center min-h-screen",
        ),
        class_name="font-['JetBrains_Mono'] bg-gray-50",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index)
app.add_page(login_page, route="/admin")
app.add_page(dashboard_page, route="/admin/dashboard", on_load=AdminState.check_auth)
from fastapi import FastAPI
from .database import create_db_and_tables

api = FastAPI()


@api.on_event("startup")
def on_startup():
    create_db_and_tables()


api.add_api_route("/api/feedback", api_routes.create_feedback, methods=["POST"])
api.add_api_route("/api/feedback", api_routes.list_feedback, methods=["GET"])
api.add_api_route(
    "/api/feedback/{feedback_id}", api_routes.get_feedback_by_id, methods=["GET"]
)
api.add_api_route(
    "/api/courier/{courier_id}", api_routes.get_courier_by_id, methods=["GET"]
)
app.api = api