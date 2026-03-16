import reflex as rx
from app.pages.home import home

app = rx.App(
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="none",
        accent_color="gray"
    ),
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Lato:wght@300;400;700;900&display=swap"
    ],
    style={
        "::selection": {
            "background": "#a67c52",
            "color": "#ffffff",
        },
        "a[href='https://reflex.dev']": {
            "display": "none !important",
        },
        # Hover no card: escurece imagem e mostra overlay
        ".image-card:hover img": {
            "opacity": "0.65 !important",
            "transition": "opacity 0.25s ease",
        },
        ".image-card:hover .card-overlay": {
            "opacity": "1 !important",
        },
        ".image-card img": {
            "transition": "opacity 0.25s ease",
        },
    }
)

app.add_page(
    home,
    route="/",
    title="Firmato - Buscador de Imagens",
    description="Buscador de imagens elegante inspirado no design Firmato",
)