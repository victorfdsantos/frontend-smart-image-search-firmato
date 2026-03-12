import reflex as rx

config = rx.Config(
    app_name="app",
    frontend_port=3000,
    backend_port=8001,
    api_url="http://localhost:8001",
    deploy_url="http://localhost",
    disable_plugins=[
        'reflex.plugins.sitemap.SitemapPlugin',
    ],
    telemetry_enabled=False,
)