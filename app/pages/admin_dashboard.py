import reflex as rx
from ..states.admin_state import AdminState


def header() -> rx.Component:
    return rx.el.header(
        rx.el.div(
            rx.el.div(
                rx.icon("layout-dashboard", class_name="h-6 w-6 text-blue-600"),
                rx.el.h1("Admin Dashboard", class_name="text-xl font-bold font-mono"),
                class_name="flex items-center gap-3",
            ),
            rx.el.button(
                rx.icon("log-out", class_name="h-4 w-4 mr-2"),
                "Logout",
                on_click=AdminState.logout,
                class_name="flex items-center bg-red-500 text-white font-mono text-sm py-2 px-4 rounded-lg hover:bg-red-600 transition-colors",
            ),
            class_name="container mx-auto flex items-center justify-between p-4",
        ),
        class_name="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-10",
    )


def filters() -> rx.Component:
    return rx.el.div(
        rx.el.h3("Filters", class_name="text-lg font-semibold font-mono mb-4"),
        rx.el.div(
            rx.el.div(
                rx.el.label("From Date", class_name="font-mono text-sm font-medium"),
                rx.el.input(
                    type="date",
                    on_change=AdminState.set_filter_from_date,
                    value=AdminState.filter_from_date,  # FIXED: Use value instead of default_value
                    class_name="w-full p-2 border rounded-md font-mono",
                ),
                class_name="flex-1",
            ),
            rx.el.div(
                rx.el.label("To Date", class_name="font-mono text-sm font-medium"),
                rx.el.input(
                    type="date",
                    on_change=AdminState.set_filter_to_date,
                    value=AdminState.filter_to_date,  # FIXED: Use value
                    class_name="w-full p-2 border rounded-md font-mono",
                ),
                class_name="flex-1",
            ),
            rx.el.div(
                rx.el.label("Rating", class_name="font-mono text-sm font-medium"),
                rx.el.div(
                    rx.foreach(
                        [1, 2, 3, 4, 5],
                        lambda r: rx.el.button(
                            f"{r} ★",
                            on_click=lambda: AdminState.toggle_rating_filter(r),
                            class_name=rx.cond(
                                AdminState.filter_ratings.contains(r),
                                "bg-blue-600 text-white px-3 py-1 rounded-full text-sm font-mono",
                                "bg-gray-200 text-gray-700 px-3 py-1 rounded-full text-sm font-mono hover:bg-gray-300",
                            ),
                        ),
                    ),
                    class_name="flex items-center gap-2",
                ),
                class_name="col-span-2 md:col-span-1",
            ),
            rx.el.div(
                rx.el.button(
                    "Reset",
                    on_click=AdminState.reset_filters,
                    class_name="w-full bg-gray-500 text-white font-mono py-2 px-4 rounded-lg hover:bg-gray-600",
                ),
                rx.el.button(
                    rx.icon("download", class_name="h-4 w-4 mr-2"),
                    "Export CSV",
                    on_click=AdminState.get_csv,
                    class_name="w-full flex items-center justify-center bg-green-600 text-white font-mono py-2 px-4 rounded-lg hover:bg-green-700",
                ),
                class_name="flex gap-2 items-end col-span-2 md:col-span-1",
            ),
            class_name="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6",
        ),
        class_name="bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-6",
    )


def feedback_table() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.foreach(
                            [
                                "ID",
                                "Order ID",
                                "Courier",
                                "Rating",
                                "Comment",
                                "Reasons",
                                "Consent",
                                "Follow-up",
                                "Date",
                            ],
                            lambda col: rx.el.th(
                                col,
                                class_name="p-3 text-left text-xs font-mono font-semibold uppercase text-gray-500",
                            ),
                        ),
                        class_name="bg-gray-50",
                    )
                ),
                rx.el.tbody(rx.foreach(AdminState.parsed_feedbacks, feedback_row)),
                class_name="min-w-full divide-y divide-gray-200",
            ),
            class_name="overflow-x-auto rounded-lg border border-gray-200 shadow-sm",
        ),
        rx.cond(
            AdminState.filtered_feedbacks.length() == 0,
            rx.el.div(
                rx.el.p(
                    "No feedback found matching your criteria.",
                    class_name="text-center text-gray-500 font-mono py-10",
                ),
                class_name="bg-white rounded-lg",
            ),
        ),
    )


def feedback_row(feedback: dict) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            feedback["id"].to_string(),
            class_name="p-3 text-sm font-mono text-gray-700 whitespace-nowrap",
        ),
        rx.el.td(
            feedback["order_id"],
            class_name="p-3 text-sm font-mono text-gray-700 whitespace-nowrap",
        ),
        rx.el.td(
            feedback["courier_name"],
            class_name="p-3 text-sm font-mono text-gray-700 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.div(
                rx.foreach(
                    range(5),
                    lambda i: rx.icon(
                        "star",
                        fill=rx.cond(
                            feedback["rating"].to(int) > i, "#FBBF24", "#E5E7EB"
                        ),
                        class_name="h-5 w-5",
                    ),
                ),
                class_name="flex",
            ),
            class_name="p-3",
        ),
        rx.el.td(
            rx.el.p(feedback["comment"], class_name="max-w-xs truncate"),
            class_name="p-3 text-sm font-mono text-gray-600",
        ),
        rx.el.td(
            rx.el.div(
                rx.foreach(
                    feedback["reasons"].to(list[str]),
                    lambda reason: rx.el.span(
                        reason,
                        class_name="bg-blue-100 text-blue-800 text-xs font-mono mr-2 px-2.5 py-0.5 rounded-full",
                    ),
                ),
                class_name="flex flex-wrap gap-1",
            ),
            class_name="p-3",
        ),
        rx.el.td(
            rx.cond(
                feedback["publish_consent"],
                rx.icon("check_check", class_name="h-5 w-5 text-green-500"),
                rx.icon("circle_x", class_name="h-5 w-5 text-gray-400"),
            ),
            class_name="p-3 text-center",
        ),
        rx.el.td(
            rx.cond(
                feedback["needs_follow_up"],
                rx.el.span(
                    "Yes",
                    class_name="bg-yellow-100 text-yellow-800 text-xs font-mono font-bold px-2 py-1 rounded-full",
                ),
                rx.el.span("No", class_name="text-gray-500 text-xs font-mono"),
            ),
            class_name="p-3 text-center",
        ),
        rx.el.td(
            # FIXED: Better date formatting
            rx.cond(
                feedback["created_at"],
                feedback["created_at"].to(str).split(".")[0],
                "N/A"
            ),
            class_name="p-3 text-sm font-mono text-gray-500 whitespace-nowrap",
        ),
        class_name="hover:bg-gray-50 transition-colors",
    )


# FIXED: Wrap in function that adds on_load
def dashboard_page() -> rx.Component:
    """Admin dashboard page with authentication check."""
    return rx.el.div(
        header(),
        rx.el.main(
            filters(),
            feedback_table(),
            class_name="container mx-auto p-4 md:p-6"
        ),
        class_name="bg-gray-50 min-h-screen font-['JetBrains_Mono']",
        on_mount=AdminState.check_auth_and_load,  # FIXED: Add auth check on mount
    )
