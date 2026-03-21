import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function parseFiltersFromUrl(search: string): Record<string, string[]> {
  const params = new URLSearchParams(search);
  const filters: Record<string, string[]> = {};
  params.forEach((val, key) => {
    if (key.startsWith("f_") && val) {
      const field = key.slice(2);
      filters[field] = val.split(",").filter(Boolean);
    }
  });
  return filters;
}

export function buildSearchUrl(opts: {
  q?: string;
  page?: number;
  img?: string;
  filters?: Record<string, string[]>;
}): string {
  const parts: string[] = [];
  if (opts.q) parts.push(`q=${encodeURIComponent(opts.q)}`);
  if (opts.page && opts.page > 1) parts.push(`page=${opts.page}`);
  if (opts.img) parts.push(`img=${encodeURIComponent(opts.img)}`);
  if (opts.filters) {
    for (const [k, vals] of Object.entries(opts.filters)) {
      if (vals.length > 0)
        parts.push(`f_${k}=${encodeURIComponent(vals.join(","))}`);
    }
  }
  return parts.length ? `/?${parts.join("&")}` : "/";
}
