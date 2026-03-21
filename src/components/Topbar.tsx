import Image from "next/image";
import { Upload } from "lucide-react";
import { Button } from "@/components/ui/Button";

interface TopbarProps {
  onImport: () => void;
}

export function Topbar({ onImport }: TopbarProps) {
  return (
    <header className="sticky top-0 z-40 w-full bg-firmato-surface border-b border-firmato-border">
      <div className="flex items-center justify-between px-10 py-5">
        {/* Logo — coloque logo_cinza.png dentro de public/ */}
        <div className="h-10 flex items-center">
          <Image
            src="/logo_cinza.png"
            alt="Firmato"
            width={160}
            height={40}
            className="h-10 w-auto object-contain"
            priority
            onError={(e) => {
              // Fallback para texto caso a imagem não exista
              const target = e.currentTarget as HTMLImageElement;
              target.style.display = "none";
              const parent = target.parentElement;
              if (parent && !parent.querySelector("span")) {
                const span = document.createElement("span");
                span.className =
                  "font-lato text-2xl font-black uppercase tracking-wider text-firmato-text select-none";
                span.textContent = "Firmato";
                parent.appendChild(span);
              }
            }}
          />
        </div>

        <div className="flex items-center gap-3">
          <Button variant="solid" onClick={onImport}>
            <Upload size={14} />
            Importar Dados
          </Button>
          <Button variant="outline">Sobre</Button>
        </div>
      </div>
    </header>
  );
}
