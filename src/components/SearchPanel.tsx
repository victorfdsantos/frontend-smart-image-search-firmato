"use client";
import { useRef, useState } from "react";
import { Search, Upload, X, Plus } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { FilterDropdown } from "@/components/FilterDropdown";
import { AppliedFilters } from "@/components/AppliedFilters";
import type { FilterMap } from "@/types";

interface SearchPanelProps {
  searchText: string;
  onSearchChange: (text: string) => void;
  uploadedImage: string;
  onImageUpload: (file: File) => void;
  onImageClear: () => void;
  filters: FilterMap;
  onFilterToggle: (field: string, value: string) => void;
  onFilterRemove: (field: string, value: string) => void;
  onFilterClearAll: () => void;
  onClearAll: () => void;
}

export function SearchPanel({
  searchText,
  onSearchChange,
  uploadedImage,
  onImageUpload,
  onImageClear,
  filters,
  onFilterToggle,
  onFilterRemove,
  onFilterClearAll,
  onClearAll,
}: SearchPanelProps) {
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const dropRef = useRef<HTMLDivElement>(null);
  const [dragging, setDragging] = useState(false);

  const handleFilePick = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) onImageUpload(file);
    e.target.value = "";
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith("image/")) onImageUpload(file);
  };

  return (
    <div className="space-y-4">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Search size={18} className="text-firmato-accent" />
          <h2 className="font-lato text-xl font-light text-firmato-text tracking-tight">
            Buscar Imagens
          </h2>
        </div>
        <p className="font-lato text-sm text-firmato-muted">
          Faça upload de uma imagem ou busque por texto
        </p>
      </div>

      {/* Image upload area */}
      <div
        ref={dropRef}
        onClick={() => !uploadedImage && fileRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        className={`border rounded-sm transition-all duration-200 ${
          dragging
            ? "border-firmato-accent bg-firmato-accent/5"
            : "border-dashed border-firmato-border-dark bg-firmato-bg hover:border-firmato-accent hover:bg-firmato-accent/5"
        } ${!uploadedImage ? "cursor-pointer" : ""}`}
      >
        {uploadedImage ? (
          <div className="relative p-2">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={uploadedImage}
              alt="Uploaded"
              className="w-full h-28 object-contain"
            />
            <button
              onClick={(e) => { e.stopPropagation(); onImageClear(); }}
              className="absolute top-2 right-2 bg-black/40 hover:bg-black/60 text-white rounded-full p-0.5 transition-colors"
            >
              <X size={14} />
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2 py-5 px-4">
            <Upload size={28} className="text-firmato-border-dark" />
            <p className="font-lato text-sm font-medium text-firmato-text">
              Escolher imagem
            </p>
            <p className="font-lato text-xs text-firmato-muted">
              ou arraste e solte
            </p>
          </div>
        )}
      </div>
      <input
        ref={fileRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        className="hidden"
        onChange={handleFilePick}
      />

      {/* Text search */}
      <input
        type="text"
        placeholder="Digite sua busca..."
        value={searchText}
        onChange={(e) => onSearchChange(e.target.value)}
        className="w-full border border-firmato-border-dark rounded-sm bg-firmato-surface font-lato text-sm text-firmato-text px-4 py-2.5 focus:outline-none focus:border-firmato-accent transition-colors placeholder:text-firmato-muted"
      />

      {/* Filter button + dropdown */}
      <div className="relative">
        <Button
          variant="outline"
          className="w-full"
          onClick={() => setDropdownOpen((o) => !o)}
        >
          <Plus size={14} />
          Adicionar filtro
        </Button>
        <FilterDropdown
          open={dropdownOpen}
          onClose={() => setDropdownOpen(false)}
          applied={filters}
          onToggle={(field, value) => {
            onFilterToggle(field, value);
          }}
        />
      </div>

      {/* Applied filter chips */}
      <AppliedFilters
        filters={filters}
        onRemove={onFilterRemove}
        onClearAll={onFilterClearAll}
      />

      {/* Clear all */}
      <Button variant="outline" className="w-full" onClick={onClearAll}>
        <X size={16} />
        Limpar tudo
      </Button>
    </div>
  );
}
