import reflex as rx
from reflex_base.plugins.sitemap import SitemapPlugin

config = rx.Config(
    app_name="aws_simulator",
    backend_port=8000,
    backend_host="0.0.0.0",  # Ascolta su tutte le interfacce di rete
    telemetry_enabled=False,
    show_built_with_reflex=False,
    disable_plugins=[SitemapPlugin],
)
