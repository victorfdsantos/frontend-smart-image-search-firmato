import asyncio
import base64
import urllib.parse
import reflex as rx
from pydantic import BaseModel
from app.api_client import (
    get_products, search_products, image_url,
    get_product_detail, get_filter_options,
)


class ProductSummary(BaseModel):
    id_produto: str = ""
    imagem_url: str = ""
    nome_produto: str = ""
    marca: str = ""
    categoria_principal: str = ""
    faixa_preco: str = ""
    altura_cm: str = ""
    largura_cm: str = ""
    profundidade_cm: str = ""


FILTER_FIELDS = [
    ("marca",               "Marca"),
    ("categoria_principal", "Categoria Principal"),
    ("subcategoria",        "Subcategoria"),
    ("faixa_preco",         "Faixa de Preço"),
    ("ambiente",            "Ambiente"),
    ("forma",               "Forma"),
    ("material_principal",  "Material Principal"),
]

FILTER_LABELS: dict[str, str] = {k: v for k, v in FILTER_FIELDS}


class State(rx.State):
    search_text: str = ""
    selected_image: str = ""
    selected_product: dict = {}
    page: int = 1
    page_size: int = 20
    total: int = 0
    total_pages: int = 1
    is_loading: bool = False
    is_searching: bool = False
    products: list[ProductSummary] = []
    uploaded_image: str = ""
    _image_bytes: bytes = b""

    # ------------------------------------------------------------------
    # Filtros inline
    # ------------------------------------------------------------------
    # Filtros já aplicados: {field: [val1, val2]}
    applied_filters: dict = {}
    # Valores aplicados por campo (tipados para rx.foreach nos chips)
    af_marca: list[str] = []
    af_categoria_principal: list[str] = []
    af_subcategoria: list[str] = []
    af_faixa_preco: list[str] = []
    af_ambiente: list[str] = []
    af_forma: list[str] = []
    af_material_principal: list[str] = []

    @rx.var
    def has_any_filter(self) -> bool:
        return bool(self.applied_filters)

    # Estado do dropdown inline
    filter_dropdown_open: bool = False
    # "fields" = mostrando lista de campos | "tags" = mostrando tags do campo ativo
    filter_dropdown_mode: str = "fields"
    filter_active_field: str = ""
    filter_active_field_label: str = ""
    filter_active_opts: list[str] = []
    filter_is_loading: bool = False
    filter_search_text: str = ""

    @rx.var
    def active_field_selected(self) -> list[str]:
        """Valores selecionados do campo ativo — para marcar tags no dropdown."""
        return list(self.applied_filters.get(self.filter_active_field, []))

    @rx.var
    def filter_active_opts_filtered(self) -> list[str]:
        """Opções do campo ativo filtradas pelo texto de busca."""
        if not self.filter_search_text.strip():
            return self.filter_active_opts
        q = self.filter_search_text.lower().strip()
        return [v for v in self.filter_active_opts if q in v.lower()]

    # ------------------------------------------------------------------
    # Modal de importação
    # ------------------------------------------------------------------
    show_import_modal: bool = False
    import_filename: str = ""
    is_uploading: bool = False
    is_retraining: bool = False
    upload_success: bool = False
    upload_error: str = ""
    upload_stats: dict = {}
    _excel_bytes: bytes = b""

    # ------------------------------------------------------------------
    # Dropdown de filtro
    # ------------------------------------------------------------------

    def open_filter_dropdown(self):
        self.filter_dropdown_open = True
        self.filter_dropdown_mode = "fields"
        self.filter_active_field = ""
        self.filter_active_field_label = ""
        self.filter_active_opts = []
        self.filter_search_text = ""

    def close_filter_dropdown(self):
        self.filter_dropdown_open = False

    def set_filter_search_text(self, text: str):
        self.filter_search_text = text

    @rx.event(background=True)
    async def select_filter_field(self, field: str, label: str):
        """Usuário escolheu um campo — carrega as tags disponíveis em cascata."""
        async with self:
            self.filter_active_field = field
            self.filter_active_field_label = label
            self.filter_dropdown_mode = "tags"
            self.filter_search_text = ""
            self.filter_is_loading = True

        data = await get_filter_options({})

        async with self:
            self.filter_active_opts = data.get("options", {}).get(field, [])
            self.filter_is_loading = False

    @rx.event(background=True)
    async def toggle_filter_tag(self, field: str, value: str):
        """Adiciona/remove uma tag e re-busca imediatamente."""
        import urllib.parse as _up
        async with self:
            current = list(self.applied_filters.get(field, []))
            if value in current:
                current.remove(value)
            else:
                current.append(value)
            if current:
                self.applied_filters = {**{k: list(v) for k, v in self.applied_filters.items()}, field: list(current)}
            else:
                self.applied_filters = {k: list(v) for k, v in self.applied_filters.items() if k != field}
            self._sync_af()
            self.page = 1
            has_query = bool(self.search_text.strip())
            has_image = bool(self._image_bytes)

        if has_query or has_image:
            yield State.run_search(self.search_text)
        else:
            async with self:
                await self.load_products()

        async with self:
            parts = []
            if self.search_text:
                parts.append(f"q={_up.quote_plus(self.search_text)}")
            if self.page > 1:
                parts.append(f"page={self.page}")
            if self.selected_image:
                parts.append(f"img={_up.quote_plus(self.selected_image)}")
            for fld, vals in self.applied_filters.items():
                if vals:
                    parts.append(f"f_{fld}={_up.quote_plus(','.join(vals))}")
            qs = "&".join(parts)
            url = f"/?{qs}" if qs else "/"
        yield rx.call_script(f"window.history.replaceState(null, '', '{url}');")



    def remove_filter_value(self, field: str, value: str):
        """Remove uma tag específica de um filtro via chip ×."""
        current = list(self.applied_filters.get(field, []))
        if value in current:
            current.remove(value)
        if current:
            self.applied_filters = {**self.applied_filters, field: current}
        else:
            self.applied_filters = {k: v for k, v in self.applied_filters.items() if k != field}
        self._sync_af()
        self.page = 1
        if self.search_text.strip() or self._image_bytes:
            yield State.run_search(self.search_text)
            yield self._push_url()
        else:
            yield State.reload_after_filter_remove

    @rx.event(background=True)
    async def reload_after_filter_remove(self):
        async with self:
            await self.load_products()
        yield self._push_url()

    @rx.event(background=True)
    async def clear_all_filters(self):
        async with self:
            self.applied_filters = {}
            self._sync_af()
            self.filter_dropdown_open = False
            has_query = bool(self.search_text.strip())
            has_image = bool(self._image_bytes)

        if has_query or has_image:
            yield State.run_search(self.search_text)
        else:
            async with self:
                await self.load_products()
            yield self._push_url()

    def _sync_af(self):
        """Sincroniza applied_filters → af_* vars tipadas para uso nos chips."""
        fields = ["marca","categoria_principal","subcategoria",
                  "faixa_preco","ambiente","forma","material_principal"]
        for f in fields:
            setattr(self, f"af_{f}", list(self.applied_filters.get(f, [])))

    # ------------------------------------------------------------------
    # Seleção de imagem
    # ------------------------------------------------------------------

    def select_image(self, url: str, product_id: str):
        self.selected_image = url
        self.selected_product = {}
        yield State.load_product_detail(product_id)
        yield self._push_url()

    @rx.event(background=True)
    async def load_product_detail(self, product_id: str):
        data = await get_product_detail(product_id)
        async with self:
            self.selected_product = data or {}

    # ------------------------------------------------------------------
    # Modal de importação
    # ------------------------------------------------------------------

    def open_import_modal(self):
        self.show_import_modal = True
        self.import_filename = ""
        self.is_uploading = False
        self.is_retraining = False
        self.upload_success = False
        self.upload_error = ""
        self.upload_stats = {}
        self._excel_bytes = b""

    def close_import_modal(self):
        self.show_import_modal = False

    async def handle_excel_upload(self, files: list[rx.UploadFile]):
        if not files:
            return
        file = files[0]
        self._excel_bytes = await file.read()
        self.import_filename = file.name
        self.upload_error = ""

    @rx.event(background=True)
    async def do_upload(self):
        async with self:
            if not self._excel_bytes:
                self.upload_error = "Selecione um arquivo antes de continuar."
                return
            self.is_uploading = True
            self.upload_error = ""
            excel_bytes = self._excel_bytes
            filename = self.import_filename
        try:
            import httpx
            from app.api_client import API_BASE
            async with httpx.AsyncClient(timeout=300) as client:
                resp = await client.post(
                    f"{API_BASE}/catalog/register",
                    files={"file": (filename, excel_bytes,
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
                )
                resp.raise_for_status()
                data = resp.json()
            async with self:
                self.is_uploading = False
                self.upload_success = True
                self.upload_stats = data.get("stats", {})
                self._excel_bytes = b""
        except Exception as exc:
            async with self:
                self.is_uploading = False
                self.upload_error = f"Erro: {str(exc)}"

    @rx.event(background=True)
    async def retrain_model(self):
        async with self:
            self.is_retraining = True
            self.upload_error = ""
        try:
            import httpx
            from app.api_client import API_BASE
            async with httpx.AsyncClient(timeout=600) as client:
                resp = await client.post(f"{API_BASE}/catalog/retrain")
                resp.raise_for_status()
            async with self:
                self.is_retraining = False
                self.upload_success = True
                self.upload_stats = {}
        except Exception as exc:
            async with self:
                self.is_retraining = False
                self.upload_error = f"Erro no retreinamento: {str(exc)}"

    def download_log(self):
        from app.api_client import API_BASE
        return rx.call_script(f"window.open('{API_BASE}/catalog/latest-log', '_blank');")

    # ------------------------------------------------------------------
    # Inicialização
    # ------------------------------------------------------------------

    async def on_load(self):
        yield rx.call_script("window.location.search", callback=State.restore_from_url)

    async def restore_from_url(self, search: str):
        params = dict(urllib.parse.parse_qsl(search.lstrip("?")))
        q    = params.get("q", "").strip()
        page = int(params.get("page", 1))
        img  = params.get("img", "")
        self.search_text    = q
        self.page           = max(1, page)
        self.selected_image = img
        # Restaura filtros da URL (f_campo=val1,val2)
        filters = {}
        for key, val in params.items():
            if key.startswith("f_") and val:
                field = key[2:]
                filters[field] = [v.strip() for v in urllib.parse.unquote_plus(val).split(",") if v.strip()]
        if filters:
            self.applied_filters = filters
            self._sync_af()
        if q or filters:
            yield State.run_search(q)
        else:
            await self.load_products()


    # ------------------------------------------------------------------
    # URL sync
    # ------------------------------------------------------------------

    def _push_url(self):
        parts = []
        if self.search_text:
            parts.append(f"q={urllib.parse.quote_plus(self.search_text)}")
        if self.page > 1:
            parts.append(f"page={self.page}")
        if self.selected_image:
            parts.append(f"img={urllib.parse.quote_plus(self.selected_image)}")
        for field, values in self.applied_filters.items():
            if values:
                parts.append(f"f_{field}={urllib.parse.quote_plus(','.join(values))}")
        qs  = "&".join(parts)
        url = f"/?{qs}" if qs else "/"
        return rx.call_script(f"window.history.replaceState(null, '', '{url}');")

    # ------------------------------------------------------------------
    # Upload de imagem
    # ------------------------------------------------------------------

    async def handle_upload(self, files: list[rx.UploadFile]):
        if not files:
            return
        file = files[0]
        self._image_bytes = await file.read()
        b64 = base64.b64encode(self._image_bytes).decode()
        self.uploaded_image = f"data:image/jpeg;base64,{b64}"
        yield State.run_search(self.search_text)

    async def clear_image(self):
        self._image_bytes = b""
        self.uploaded_image = ""
        if self.search_text.strip():
            yield State.run_search(self.search_text)
        else:
            await self.load_products()
            yield self._push_url()

    # ------------------------------------------------------------------
    # Busca
    # ------------------------------------------------------------------

    @rx.event(background=True)
    async def set_search_text(self, text: str):
        async with self:
            self.search_text = text
            self.page = 1
        if not text.strip() and not self._image_bytes:
            async with self:
                await self.load_products()
            yield self._push_url()
            return
        await asyncio.sleep(0.5)
        async with self:
            current_text = self.search_text
        if current_text != text:
            return
        yield State.run_search(text)

    @rx.event(background=True)
    async def run_search(self, text: str):
        async with self:
            self.is_searching = True
            image_bytes = self._image_bytes
            query = text.strip() or None
            filters = {k: list(v) for k, v in self.applied_filters.items() if v}

        data = await search_products(
            query=query,
            image_bytes=image_bytes if image_bytes else None,
            active_filters=filters if filters else None,
        )

        async with self:
            self.total       = data.get("total", 0)
            self.total_pages = 1
            self.products    = [
                ProductSummary(
                    id_produto=str(item["id_produto"]),
                    imagem_url=image_url(item["id_produto"]),
                    nome_produto=str(item.get("nome_produto") or ""),
                    marca=str(item.get("marca") or ""),
                    categoria_principal=str(item.get("categoria_principal") or ""),
                    faixa_preco=str(item.get("faixa_preco") or ""),
                    altura_cm=str(item.get("altura_cm") or ""),
                    largura_cm=str(item.get("largura_cm") or ""),
                    profundidade_cm=str(item.get("profundidade_cm") or ""),
                )
                for item in data.get("items", [])
            ]
            self.is_searching = False
        yield self._push_url()

    # ------------------------------------------------------------------
    # Galeria paginada
    # ------------------------------------------------------------------

    async def load_products(self):
        self.is_loading = True
        filters = {k: list(v) for k, v in self.applied_filters.items() if v} if self.applied_filters else None
        data = await get_products(page=self.page, page_size=self.page_size, active_filters=filters)
        self.total       = data.get("total", 0)
        self.total_pages = data.get("total_pages", 1)
        self.products    = [
            ProductSummary(
                id_produto=str(item["id_produto"]),
                imagem_url=image_url(item["id_produto"]),
                nome_produto=str(item.get("nome_produto") or ""),
                marca=str(item.get("marca") or ""),
                categoria_principal=str(item.get("categoria_principal") or ""),
                faixa_preco=str(item.get("faixa_preco") or ""),
                altura_cm=str(item.get("altura_cm") or ""),
                largura_cm=str(item.get("largura_cm") or ""),
                profundidade_cm=str(item.get("profundidade_cm") or ""),
            )
            for item in data.get("items", [])
        ]
        self.is_loading = False

    async def next_page(self):
        if self.page < self.total_pages:
            self.page += 1
            await self.load_products()
            yield self._push_url()

    async def prev_page(self):
        if self.page > 1:
            self.page -= 1
            await self.load_products()
            yield self._push_url()

    async def clear_all(self):
        self._image_bytes     = b""
        self.uploaded_image   = ""
        self.search_text      = ""
        self.page             = 1
        self.selected_image   = ""
        self.selected_product = {}
        self.applied_filters  = {}
        self._sync_af()
        self.filter_dropdown_open = False
        await self.load_products()
        yield self._push_url()

    def copy_image(self):
        return rx.call_script(f"""
            fetch('{self.selected_image}', {{mode: 'cors'}})
                .then(r => r.blob())
                .then(blob => {{
                    const item = new ClipboardItem({{'image/jpeg': blob}});
                    navigator.clipboard.write([item])
                        .then(() => console.log('Copiado!'))
                        .catch(e => console.error('Erro ao copiar:', e));
                }})
                .catch(e => console.error('Fetch falhou:', e));
        """)

    def download_image(self):
        return rx.call_script(f"""
            fetch('{self.selected_image}', {{mode: 'cors'}})
                .then(r => r.blob())
                .then(blob => {{
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = '{self.selected_image}'.split('/').pop();
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                }})
                .catch(e => console.error('Download falhou:', e));
        """)