import reflex as rx
from app.state import State, ProductSummary
from app.styles import home as styles


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def detail_field(label: str, value):
    """Linha de campo: label à esquerda, valor à direita."""
    return rx.hstack(
        rx.text(
            label,
            style=styles.get_base_text_style("12px", color=styles.COLORS["text_secondary"]),
            min_width="140px",
        ),
        rx.text(
            value,
            style=styles.get_base_text_style("12px"),
            flex="1",
        ),
        width="100%",
        padding_y="5px",
        border_bottom=f"1px solid {styles.COLORS['border']}",
        align="start",
    )


def detail_section(title: str, *fields):
    return rx.vstack(
        rx.text(
            title,
            style=styles.get_base_text_style("11px", weight="700", color=styles.COLORS["accent"]),
            text_transform="uppercase",
            letter_spacing="0.08em",
            padding_top="8px",
        ),
        *fields,
        spacing="0",
        width="100%",
    )


def product_detail_panel():
    return rx.cond(
        State.selected_product.length() > 0,
        rx.vstack(
            rx.hstack(
                rx.icon(tag="package", size=16, color=styles.COLORS["accent"]),
                rx.text(
                    "Informações do Produto",
                    style=styles.get_base_heading_style("15px"),
                ),
                spacing="2",
                align="center",
                width="100%",
            ),
            rx.divider(border_color=styles.COLORS["border"], width="100%"),

            # Identificação
            detail_section(
                "Identificação",
                detail_field("ID", State.selected_product["id_produto"]),
                detail_field("Nome", State.selected_product["nome_produto"]),
                detail_field("Marca", State.selected_product["marca"]),
                detail_field("Status", State.selected_product["status"]),
                detail_field("Categoria", State.selected_product["categoria_principal"]),
                detail_field("Subcategoria", State.selected_product["subcategoria"]),
                detail_field("Faixa de Preço", State.selected_product["faixa_preco"]),
            ),

            # Características
            detail_section(
                "Características",
                detail_field("Ambiente", State.selected_product["ambiente"]),
                detail_field("Forma", State.selected_product["forma"]),
                detail_field("Material Principal", State.selected_product["material_principal"]),
                detail_field("Material Estrutura", State.selected_product["material_estrutura"]),
                detail_field("Material Revestimento", State.selected_product["material_revestimento"]),
            ),

            # Dimensões
            detail_section(
                "Dimensões",
                detail_field("Altura (cm)", State.selected_product["altura_cm"]),
                detail_field("Largura (cm)", State.selected_product["largura_cm"]),
                detail_field("Profundidade (cm)", State.selected_product["profundidade_cm"]),
            ),

            # Descrição
            detail_section(
                "Descrição Técnica",
                rx.text(
                    State.selected_product["descricao_tecnica"],
                    style=styles.get_base_text_style("12px", color=styles.COLORS["text_secondary"]),
                    padding_y="6px",
                    white_space="pre-wrap",
                ),
            ),

            spacing="2",
            width="100%",
            padding="20px",
            background_color=styles.COLORS["background"],
            border=f"1px solid {styles.COLORS['border']}",
            margin_top="12px",
        ),
    )


# ------------------------------------------------------------------
# Modal de importação
# ------------------------------------------------------------------

def stat_row(label: str, value):
    return rx.hstack(
        rx.text(label, style=styles.get_base_text_style("13px", color=styles.COLORS["text_secondary"])),
        rx.spacer(),
        rx.text(value, style=styles.get_base_text_style("13px", weight="600")),
        width="100%",
        padding_y="4px",
        border_bottom=f"1px solid {styles.COLORS['border']}",
    )


def upload_result():
    return rx.vstack(
        rx.hstack(
            rx.icon(tag="circle-check", size=24, color="#4caf50"),
            rx.text(
                rx.cond(
                    State.upload_stats.length() > 0,
                    "Processamento concluído",
                    "Retreinamento concluído",
                ),
                style=styles.get_base_text_style("15px", weight="600"),
            ),
            spacing="2",
            align="center",
        ),
        rx.divider(border_color=styles.COLORS["border"], margin_y="4px"),
        rx.cond(
            State.upload_stats.length() > 0,
            rx.vstack(
                stat_row("Total de linhas",            State.upload_stats["total"]),
                stat_row("Novos produtos",             State.upload_stats["novos"]),
                stat_row("Imagens atualizadas",        State.upload_stats["imagem_principal_atualizada"]),
                stat_row("Secundárias processadas",    State.upload_stats["secundarias_processadas"]),
                stat_row("Secundárias deletadas",      State.upload_stats["secundarias_deletadas"]),
                stat_row("Pastas movidas no NAS",      State.upload_stats["pasta_nas_movida"]),
                stat_row("Dados atualizados",          State.upload_stats["dados_atualizados"]),
                stat_row("Ignorados (sem mudança)",    State.upload_stats["ignorados"]),
                stat_row("Erros",                      State.upload_stats["erros"]),
                stat_row("Arquivos limpos da landing", State.upload_stats["arquivos_limpos"]),
                spacing="0",
                width="100%",
            ),
            rx.text(
                "Thumbnails e embeddings foram recarregados com sucesso.",
                style=styles.get_base_text_style("13px", color=styles.COLORS["text_secondary"]),
            ),
        ),
        rx.hstack(
            rx.cond(
                State.upload_stats.length() > 0,
                rx.button(
                    rx.hstack(
                        rx.icon(tag="file-text", size=15),
                        rx.text("Baixar Log"),
                        spacing="2",
                    ),
                    on_click=State.download_log,
                    style=styles.outline_button_style,
                    flex="1",
                ),
            ),
            rx.button(
                "Fechar",
                on_click=State.close_import_modal,
                style=styles.solid_button_style,
                flex="1",
            ),
            spacing="3",
            width="100%",
            margin_top="8px",
        ),
        spacing="3",
        width="100%",
    )


def import_modal():
    return rx.cond(
        State.show_import_modal,
        rx.box(
            rx.box(
                rx.hstack(
                    rx.hstack(
                        rx.icon(tag="upload", size=18, color=styles.COLORS["accent"]),
                        rx.heading(
                            "Importar Dados",
                            style=styles.get_base_heading_style("18px"),
                        ),
                        spacing="2",
                        align="center",
                    ),
                    rx.spacer(),
                    rx.button(
                        rx.icon(tag="x", size=16),
                        on_click=State.close_import_modal,
                        variant="ghost",
                        color=styles.COLORS["text_secondary"],
                        cursor="pointer",
                        _hover={"color": styles.COLORS["text_primary"]},
                    ),
                    width="100%",
                    align="center",
                ),
                rx.divider(border_color=styles.COLORS["border"], margin_y="20px"),
                rx.cond(
                    State.is_uploading | State.is_retraining,
                    rx.center(
                        rx.vstack(
                            rx.spinner(color=styles.COLORS["accent"], size="3"),
                            rx.text(
                                rx.cond(
                                    State.is_retraining,
                                    "Retreinando modelo...",
                                    "Processando planilha...",
                                ),
                                style=styles.get_base_text_style("14px", weight="500"),
                            ),
                            rx.text(
                                rx.cond(
                                    State.is_retraining,
                                    "Reconstruindo thumbnails e recarregando embeddings.",
                                    "Isso pode levar alguns minutos.",
                                ),
                                style=styles.get_base_text_style("12px", color=styles.COLORS["text_secondary"]),
                            ),
                            spacing="3",
                            align="center",
                        ),
                        padding_y="40px",
                        width="100%",
                    ),
                    rx.cond(
                        State.upload_success,
                        upload_result(),
                        rx.vstack(
                            rx.upload(
                                rx.vstack(
                                    rx.cond(
                                        State.import_filename != "",
                                        rx.vstack(
                                            rx.icon(tag="file-spreadsheet", size=32, color=styles.COLORS["accent"]),
                                            rx.text(
                                                State.import_filename,
                                                style=styles.get_base_text_style("13px", weight="500"),
                                            ),
                                            rx.text(
                                                "Clique para trocar o arquivo",
                                                style=styles.get_base_text_style("12px", color=styles.COLORS["text_secondary"]),
                                            ),
                                            spacing="2",
                                            align="center",
                                        ),
                                        rx.vstack(
                                            rx.icon(tag="file-up", size=32, color=styles.COLORS["border_dark"]),
                                            rx.text(
                                                "Arraste ou clique para selecionar",
                                                style=styles.get_base_text_style("13px", weight="500"),
                                            ),
                                            rx.text(
                                                "Aceita .xlsx e .xlsm",
                                                style=styles.get_base_text_style("12px", color=styles.COLORS["text_secondary"]),
                                            ),
                                            spacing="2",
                                            align="center",
                                        ),
                                    ),
                                    padding="28px 16px",
                                    width="100%",
                                    align="center",
                                ),
                                on_drop=State.handle_excel_upload,
                                accept={
                                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
                                    "application/vnd.ms-excel.sheet.macroEnabled.12": [".xlsm"],
                                },
                                border=f"1px dashed {styles.COLORS['border_dark']}",
                                border_radius="2px",
                                background_color=styles.COLORS["background"],
                                width="100%",
                                _hover={"border_color": styles.COLORS["accent"]},
                            ),
                            rx.cond(
                                State.upload_error != "",
                                rx.text(
                                    State.upload_error,
                                    style=styles.get_base_text_style("12px", color="#e53935"),
                                ),
                            ),
                            rx.hstack(
                                rx.button(
                                    rx.hstack(
                                        rx.icon(tag="upload", size=15),
                                        rx.text("Realizar Upload"),
                                        spacing="2",
                                    ),
                                    on_click=State.do_upload,
                                    style=styles.solid_button_style,
                                    flex="1",
                                ),
                                rx.button(
                                    rx.hstack(
                                        rx.icon(tag="brain", size=15),
                                        rx.text("Retreinar Modelo"),
                                        spacing="2",
                                    ),
                                    on_click=State.retrain_model,
                                    style=styles.outline_button_style,
                                    flex="1",
                                ),
                                spacing="3",
                                width="100%",
                            ),
                            spacing="4",
                            width="100%",
                        ),
                    ),
                ),
                background_color=styles.COLORS["surface"],
                border=f"1px solid {styles.COLORS['border']}",
                padding="28px",
                width="480px",
                max_width="90vw",
                on_click=rx.stop_propagation,
            ),
            position="fixed",
            top="0",
            left="0",
            width="100vw",
            height="100vh",
            background_color="rgba(0,0,0,0.45)",
            display="flex",
            align_items="center",
            justify_content="center",
            z_index="1000",
            on_click=State.close_import_modal,
        ),
    )


def topbar():
    return rx.hstack(
        rx.image(
            src="/logo_cinza.png",
            height="40px",
            width="auto",
            alt="Firmato",
        ),
        rx.spacer(),
        rx.hstack(
            rx.button(
                "Importar Dados",
                on_click=State.open_import_modal,
                style=styles.outline_button_style,
            ),
            rx.button(
                "Sobre",
                style=styles.outline_button_style,
            ),
            spacing="3",
        ),
        style=styles.topbar_style,
    )


def search_panel():
    return rx.vstack(
        rx.hstack(
            rx.icon(tag="search", size=20, color=styles.COLORS["accent"]),
            rx.heading(
                "Buscar Imagens",
                style=styles.get_base_heading_style("20px"),
            ),
            spacing="2",
            align="center",
            width="100%",
        ),
        rx.text(
            "Faça upload de uma imagem ou busque por texto",
            style=styles.get_base_text_style("14px", color=styles.COLORS["text_secondary"]),
        ),
        rx.upload(
            rx.vstack(
                rx.cond(
                    State.uploaded_image != "",
                    rx.box(
                        rx.image(
                            src=State.uploaded_image,
                            width="100%",
                            height="120px",
                            object_fit="contain",
                        ),
                        rx.button(
                            "✕ Remover",
                            on_click=State.clear_image,
                            size="1",
                            variant="ghost",
                            color=styles.COLORS["text_secondary"],
                        ),
                        width="100%",
                        position="relative",
                    ),
                    rx.vstack(
                        rx.button(
                            rx.hstack(
                                rx.icon(tag="upload", size=16),
                                rx.text("Escolher imagem"),
                                spacing="2",
                            ),
                            style=styles.solid_button_style,
                            width="100%",
                        ),
                        rx.text(
                            "ou arraste e solte",
                            style=styles.get_base_text_style("12px", color=styles.COLORS["text_secondary"]),
                        ),
                        spacing="2",
                        width="100%",
                        padding="12px",
                        align="center",
                    ),
                ),
            ),
            on_drop=State.handle_upload,
            accept={"image/jpeg": [".jpg", ".jpeg"], "image/png": [".png"], "image/webp": [".webp"]},
            border=f"1px dashed {styles.COLORS['border_dark']}",
            border_radius="2px",
            background_color=styles.COLORS["background"],
            padding="0",
            width="100%",
        ),
        rx.input(
            placeholder="Digite sua busca...",
            value=State.search_text,
            on_change=State.set_search_text,
            border=f"1px solid {styles.COLORS['border_dark']}",
            border_radius="2px",
            background_color=styles.COLORS["surface"],
            color=styles.COLORS["text_primary"],
            placeholder_color=styles.COLORS["text_primary"],
            padding="6px 16px",
            font_family="Inter, sans-serif",
            font_size="14px",
            _focus={
                "border_color": styles.COLORS["accent"],
                "border_width": "1px",
                "box_shadow": f"0 0 0 2px {styles.COLORS['accent_light']}20",
                "outline": "none",
            },
            _hover={"border_color": styles.COLORS["accent"]},
            width="100%",
        ),
        rx.button(
            rx.hstack(
                rx.icon(tag="filter", size=16),
                rx.text("Filtros avançados"),
                spacing="2",
            ),
            style=styles.outline_button_style,
            width="100%",
        ),
        rx.button(
            rx.hstack(
                rx.icon(tag="x", size=20),
                rx.text("Limpar filtros"),
                spacing="2",
            ),
            on_click=State.clear_all,
            style=styles.outline_button_style,
            width="100%",
        ),
        spacing="4",
        width="100%",
    )


def image_card(product: ProductSummary):
    has_dims = product.altura_cm != ""

    overlay_content = rx.vstack(
        rx.text(
            product.nome_produto,
            style=styles.get_base_text_style("13px", weight="600", color="#ffffff"),
            no_of_lines=2,
        ),
        rx.text(
            product.marca,
            style=styles.get_base_text_style("11px", color="rgba(255,255,255,0.8)"),
        ),
        rx.text(
            product.categoria_principal,
            style=styles.get_base_text_style("11px", color="rgba(255,255,255,0.7)"),
        ),
        rx.cond(
            product.faixa_preco != "",
            rx.text(
                product.faixa_preco,
                style=styles.get_base_text_style("11px", weight="600", color=styles.COLORS["accent_light"]),
            ),
        ),
        rx.cond(
            has_dims,
            rx.text(
                product.altura_cm + " × " + product.largura_cm + " × " + product.profundidade_cm + " cm",
                style=styles.get_base_text_style("10px", color="rgba(255,255,255,0.6)"),
            ),
        ),
        spacing="1",
        align="start",
        width="100%",
    )

    return rx.box(
        rx.image(
            src=product.imagem_url,
            width="100%",
            height="240px",
            object_fit="cover",
            loading="lazy",
            style={
                "animation": "fadeIn 0.35s ease forwards",
                "opacity": "0",
                "transition": "opacity 0.3s ease",
                "@keyframes fadeIn": {
                    "from": {"opacity": "0", "transform": "translateY(6px)"},
                    "to": {"opacity": "1", "transform": "translateY(0)"},
                },
            },
        ),
        # Overlay que aparece no hover
        rx.box(
            overlay_content,
            position="absolute",
            bottom="0",
            left="0",
            right="0",
            padding="12px",
            background="linear-gradient(to top, rgba(0,0,0,0.82) 0%, rgba(0,0,0,0.4) 100%, transparent 100%)",
            opacity="0",
            transition="opacity 0.25s ease",
            class_name="card-overlay",
        ),
        position="relative",
        overflow="hidden",
        class_name="image-card",
        style=styles.image_card_style,
        on_click=State.select_image(product.imagem_url, product.id_produto),
    )


def image_grid():
    return rx.cond(
        State.products.length() > 0,
        rx.grid(
            rx.foreach(State.products, image_card),
            columns="3",
            spacing="4",
            width="100%",
            key=State.search_text + State.page.to_string(),
        ),
        rx.center(
            rx.vstack(
                rx.icon(tag="image", size=48, color=styles.COLORS["border_dark"]),
                rx.text(
                    "Nenhum produto encontrado",
                    style=styles.get_base_text_style("16px", color=styles.COLORS["text_secondary"]),
                ),
                spacing="4",
            ),
            padding="48px",
            width="100%",
        ),
    )


def pagination_controls():
    return rx.hstack(
        rx.button(
            rx.hstack(
                rx.icon(tag="chevron-left", size=16),
                rx.text("Anterior"),
                spacing="1",
            ),
            on_click=State.prev_page,
            style=styles.pagination_button_style,
            is_disabled=State.page <= 1,
        ),
        rx.text(
            f"{State.page} / {State.total_pages}",
            style=styles.get_base_text_style("14px", color=styles.COLORS["text_secondary"]),
            min_width="60px",
            text_align="center",
        ),
        rx.button(
            rx.hstack(
                rx.text("Próxima"),
                rx.icon(tag="chevron-right", size=16),
                spacing="1",
            ),
            on_click=State.next_page,
            style=styles.pagination_button_style,
            is_disabled=State.page >= State.total_pages,
        ),
        spacing="4",
        justify="center",
        width="100%",
    )


def preview_panel():
    return rx.vstack(
        rx.hstack(
            rx.icon(tag="eye", size=20, color=styles.COLORS["accent"]),
            rx.heading(
                "Pré-visualização",
                style=styles.get_base_heading_style("20px"),
            ),
            spacing="2",
            align="center",
            width="100%",
        ),
        rx.divider(border_color=styles.COLORS["border"], width="100%"),
        rx.cond(
            State.selected_image != "",
            rx.vstack(
                rx.box(
                    rx.image(
                        src=State.selected_image,
                        width="100%",
                        max_height="600px",
                        object_fit="contain",
                        border_radius="2px",
                    ),
                    border=f"1px solid {styles.COLORS['border']}",
                    padding="4px",
                    width="100%",
                ),
                rx.hstack(
                    rx.button(
                        rx.hstack(
                            rx.icon(tag="copy", size=16),
                            rx.text("Copiar imagem"),
                            spacing="2",
                        ),
                        on_click=State.copy_image,
                        style=styles.outline_button_style,
                        flex="1",
                    ),
                    rx.button(
                        rx.hstack(
                            rx.icon(tag="download", size=16),
                            rx.text("Download"),
                            spacing="2",
                        ),
                        on_click=State.download_image,
                        style=styles.solid_button_style,
                        flex="1",
                    ),
                    spacing="3",
                    width="100%",
                ),
                # Detalhes do produto abaixo da imagem
                product_detail_panel(),
                spacing="4",
                width="100%",
            ),
            rx.center(
                rx.vstack(
                    rx.icon(tag="image", size=64, color=styles.COLORS["border"]),
                    rx.text(
                        "Selecione uma imagem",
                        style=styles.get_base_text_style("16px", color=styles.COLORS["text_secondary"]),
                    ),
                    rx.text(
                        "Clique em qualquer imagem para visualizar",
                        style=styles.get_base_text_style("14px", color=styles.COLORS["text_secondary"]),
                    ),
                    spacing="3",
                ),
                height="600px",
                width="100%",
                border=f"2px dashed {styles.COLORS['border']}",
                background_color=styles.COLORS["background"],
                padding="48px",
            ),
        ),
        style=styles.panel_style,
        width="100%",
        spacing="4",
    )


def left_panel():
    return rx.vstack(
        search_panel(),
        rx.divider(border_color=styles.COLORS["border"], width="100%"),
        rx.hstack(
            rx.text(
                "Resultados",
                style=styles.get_base_text_style("16px", weight="500"),
            ),
            rx.spacer(),
            rx.text(
                State.total.to_string() + " produtos",
                style=styles.get_base_text_style("14px", color=styles.COLORS["text_secondary"]),
            ),
            width="100%",
        ),
        image_grid(),
        pagination_controls(),
        style=styles.panel_style,
        width="100%",
        spacing="5",
    )


def home():
    return rx.box(
        import_modal(),
        rx.vstack(
            topbar(),
            rx.hstack(
                rx.box(
                    left_panel(),
                    flex="0 0 38%",
                    padding="32px 16px 32px 32px",
                ),
                rx.box(
                    preview_panel(),
                    flex="1",
                    padding="32px 32px 32px 16px",
                ),
                width="100%",
                align_items="stretch",
                spacing="0",
            ),
            width="100%",
            background_color=styles.COLORS["background"],
            min_height="100vh",
            spacing="0",
            on_mount=State.on_load,
        ),
        position="relative",
    )