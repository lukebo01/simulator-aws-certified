import reflex as rx
from reflex_base.plugins.sitemap import SitemapPlugin

config = rx.Config(
    app_name="aws_simulator",
    backend_port=8000,
    backend_host="127.0.0.1",
    telemetry_enabled=False,
    show_built_with_reflex=False,
    disable_plugins=[SitemapPlugin],
)
