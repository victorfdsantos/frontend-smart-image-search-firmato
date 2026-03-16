import asyncio
import base64
import urllib.parse
import reflex as rx
from pydantic import BaseModel
from app.api_client import get_products, search_products, image_url, get_product_detail


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

    # Modal de importação
    show_import_modal: bool = False
    import_filename: str = ""
    is_uploading: bool = False
    is_retraining: bool = False
    upload_success: bool = False
    upload_error: str = ""
    upload_stats: dict = {}
    _excel_bytes: bytes = b""

    # ------------------------------------------------------------------
    # Seleção de imagem + carrega detalhes do produto
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
        return rx.call_script(
            f"window.open('{API_BASE}/catalog/latest-log', '_blank');"
        )

    # ------------------------------------------------------------------
    # Inicialização
    # ------------------------------------------------------------------

    async def on_load(self):
        yield rx.call_script(
            "window.location.search",
            callback=State.restore_from_url,
        )

    async def restore_from_url(self, search: str):
        params = dict(urllib.parse.parse_qsl(search.lstrip("?")))
        q    = params.get("q", "").strip()
        page = int(params.get("page", 1))
        img  = params.get("img", "")
        self.search_text    = q
        self.page           = max(1, page)
        self.selected_image = img
        if q:
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
    # Busca com debounce
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
        data = await search_products(
            query=query,
            image_bytes=image_bytes if image_bytes else None,
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
        data = await get_products(page=self.page, page_size=self.page_size)
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
        self._image_bytes    = b""
        self.uploaded_image  = ""
        self.search_text     = ""
        self.page            = 1
        self.selected_image  = ""
        self.selected_product = {}
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