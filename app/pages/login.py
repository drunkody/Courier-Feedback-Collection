import reflex as rx
from ..states.admin_state import AdminState


def login_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h1(
                "Admin Login",
                class_name="text-2xl font-bold text-gray-800 mb-6 text-center font-mono",
            ),
            rx.el.form(
                rx.el.div(
                    rx.el.label(
                        "Username",
                        class_name="block text-sm font-medium text-gray-700 font-mono mb-1",
                    ),
                    rx.el.input(
                        placeholder="admin",
                        name="username",
                        class_name="w-full p-2 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 font-mono",
                    ),
                    class_name="mb-4",
                ),
                rx.el.div(
                    rx.el.label(
                        "Password",
                        class_name="block text-sm font-medium text-gray-700 font-mono mb-1",
                    ),
                    rx.el.input(
                        type="password",
                        placeholder="••••••••",
                        name="password",
                        class_name="w-full p-2 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 font-mono",
                    ),
                    class_name="mb-4",
                ),
                rx.cond(
                    AdminState.error_message != "",
                    rx.el.p(
                        AdminState.error_message,
                        class_name="text-red-500 text-sm mb-4 font-mono",
                    ),
                ),
                rx.el.button(
                    "Login",
                    type="submit",
                    class_name="w-full bg-blue-600 text-white font-bold py-2 px-4 rounded-lg shadow-md hover:bg-blue-700 disabled:opacity-50 transition-colors font-mono",
                ),
                on_submit=AdminState.login,
            ),
            class_name="w-full max-w-sm bg-white p-8 rounded-xl shadow-lg border border-gray-200",
        ),
        class_name="flex items-center justify-center min-h-screen bg-gray-50 font-['JetBrains_Mono']",
    )