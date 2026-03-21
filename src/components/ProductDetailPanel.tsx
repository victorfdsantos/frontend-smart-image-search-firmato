"use client";
import type { ProductDetail } from "@/types";

interface DetailFieldProps {
  label: string;
  value?: string | number | null;
}

function DetailField({ label, value }: DetailFieldProps) {
  if (!value) return null;
  return (
    <div className="flex py-1.5 border-b border-firmato-border last:border-b-0">
      <span className="font-lato text-xs text-firmato-muted min-w-[140px] shrink-0">
        {label}
      </span>
      <span className="font-lato text-xs text-firmato-text flex-1">{value}</span>
    </div>
  );
}

interface SectionProps {
  title: string;
  children: React.ReactNode;
}

function Section({ title, children }: SectionProps) {
  return (
    <div className="space-y-0">
      <p className="font-lato text-[11px] font-bold text-firmato-accent uppercase tracking-widest pt-2 pb-1">
        {title}
      </p>
      {children}
    </div>
  );
}

interface ProductDetailPanelProps {
  product: ProductDetail;
}

export function ProductDetailPanel({ product }: ProductDetailPanelProps) {
  return (
    <div className="mt-3 p-5 bg-firmato-bg border border-firmato-border space-y-1">
      <div className="flex items-center gap-2 mb-3">
        <h3 className="font-lato text-[15px] font-light text-firmato-text tracking-tight">
          Informações do Produto
        </h3>
      </div>
      <div className="border-t border-firmato-border" />

      <div className="space-y-2 pt-1">
        <Section title="Identificação">
          <DetailField label="ID" value={String(product.id_produto)} />
          <DetailField label="Nome" value={product.nome_produto} />
          <DetailField label="Marca" value={product.marca} />
          <DetailField label="Status" value={product.status} />
          <DetailField label="Categoria" value={product.categoria_principal} />
          <DetailField label="Subcategoria" value={product.subcategoria} />
          <DetailField label="Faixa de Preço" value={product.faixa_preco} />
        </Section>

        <Section title="Características">
          <DetailField label="Ambiente" value={product.ambiente} />
          <DetailField label="Forma" value={product.forma} />
          <DetailField label="Material Principal" value={product.material_principal} />
          <DetailField label="Material Estrutura" value={product.material_estrutura} />
          <DetailField label="Material Revestimento" value={product.material_revestimento} />
        </Section>

        <Section title="Dimensões">
          <DetailField label="Altura (cm)" value={product.altura_cm} />
          <DetailField label="Largura (cm)" value={product.largura_cm} />
          <DetailField label="Profundidade (cm)" value={product.profundidade_cm} />
        </Section>

        {product.descricao_tecnica && (
          <Section title="Descrição Técnica">
            <p className="font-lato text-xs text-firmato-muted py-1.5 whitespace-pre-wrap leading-relaxed">
              {product.descricao_tecnica}
            </p>
          </Section>
        )}
      </div>
    </div>
  );
}
