"use client";
import { useState } from "react";
import { Upload } from "lucide-react";
import { Button } from "@/components/ui/Button";

interface TopbarProps {
  onImport: () => void;
}

function LogoSvg() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="160"
      height="40"
      viewBox="0 0 160 40"
      aria-label="Firmato"
    >
      <text
        x="0"
        y="30"
        fontFamily="Georgia, serif"
        fontSize="26"
        fontWeight="900"
        letterSpacing="3"
        fill="#2c2c2c"
      >
        FIRMATO
      </text>
    </svg>
  );
}

function Logo() {
  const [useFallback, setUseFallback] = useState(false);

  if (useFallback) return <LogoSvg />;

  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src="/logo_cinza.png"
      alt="Firmato"
      height={40}
      className="h-10 w-auto object-contain"
      onError={() => setUseFallback(true)}
    />
  );
}

export function Topbar({ onImport }: TopbarProps) {
  return (
    <header className="sticky top-0 z-40 w-full bg-firmato-surface border-b border-firmato-border">
      <div className="flex items-center justify-between px-10 py-5">
        <Logo />
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
