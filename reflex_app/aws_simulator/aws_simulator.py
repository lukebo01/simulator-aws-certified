"""Entry point dell'applicazione AWS Simulator."""
import reflex as rx

# Importa le pagine
from aws_simulator.pages.home import home_page  # noqa: F401
from aws_simulator.pages.quiz import quiz_page  # noqa: F401


def _meta_favicon() -> rx.Component:
    """Favicon meta tag."""
    return rx.script(
        """
        const link = document.createElement('link');
        link.rel = 'icon';
        link.type = 'image/x-icon';
        link.href = '/favicon.ico';
        document.head.appendChild(link);
        """,
        on_load=True,
    )


app = rx.App(
    style={
        "font_family": (
            "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', "
            "Roboto, Oxygen, Ubuntu, sans-serif"
        ),
        "::selection": {
            "background_color": "rgba(255, 153, 0, 0.2)",
        },
        "body": {
            "margin": "0",
            "padding": "0",
            "background": "linear-gradient(135deg, #f8f9fa 0%, #e8f0fe 100%)",
        },
    },
)
