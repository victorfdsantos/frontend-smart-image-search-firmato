import type {
  PaginatedProducts,
  ProductDetail,
  SearchResult,
  FilterOptions,
  FilterMap,
} from "@/types";

// Client-side: calls go to /api/* which Next.js rewrites → backend
// Server-side: calls go directly to API_BASE (e.g. http://firmato-api:8000)
const getApiBase = () => {
  if (typeof window !== "undefined") {
    return "/api";
  }
  return process.env.API_BASE ?? "http://localhost:8000";
};

// Paths passed to apiFetch must NOT include /api prefix —
// client adds it via getApiBase(), server calls backend directly.
// e.g. apiFetch("/products") →
//   client:  fetch("/api/products")   → rewrite → backend/products
//   server:  fetch("http://firmato-api:8000/products")
const buildFilterParams = (filters: FilterMap): Record<string, string> => {
  const params: Record<string, string> = {};
  for (const [k, vals] of Object.entries(filters)) {
    if (vals.length > 0) params[k] = vals.join(",");
  }
  return params;
};

async function apiFetch<T>(
  path: string,
  options?: RequestInit,
  params?: Record<string, string>
): Promise<T | null> {
  try {
    const base = getApiBase();
    // Build query string using URL for safety, but keep path separate from base
    const url = new URL(`http://placeholder${path}`);
    if (params) {
      Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
    }
    const res = await fetch(`${base}${url.pathname}${url.search}`, {
      ...options,
      cache: "no-store",
    });
    if (!res.ok) return null;
    return res.json() as Promise<T>;
  } catch {
    return null;
  }
}

export async function getProducts(
  page = 1,
  pageSize = 20,
  filters: FilterMap = {}
): Promise<PaginatedProducts> {
  const params: Record<string, string> = {
    page: String(page),
    page_size: String(pageSize),
    ...buildFilterParams(filters),
  };
  const data = await apiFetch<PaginatedProducts>("/products", undefined, params);
  return (
    data ?? { page, page_size: pageSize, total: 0, total_pages: 1, items: [] }
  );
}

export async function getProductDetail(
  id: string | number
): Promise<ProductDetail | null> {
  return apiFetch<ProductDetail>(`/products/${id}`);
}

export async function getFilterOptions(
  activeFilters: FilterMap = {}
): Promise<FilterOptions> {
  const params = buildFilterParams(activeFilters);
  const data = await apiFetch<FilterOptions>(
    "/filters/options",
    undefined,
    params
  );
  return data ?? { fields: [], labels: {}, options: {}, active_filters: {} };
}

export async function searchProducts(
  query?: string,
  imageFile?: File | null,
  topK = 20,
  filters: FilterMap = {}
): Promise<SearchResult> {
  try {
    const base = getApiBase();
    const url = new URL(`http://placeholder/search`);
    if (query?.trim()) url.searchParams.set("q", query.trim());
    url.searchParams.set("top_k", String(topK));
    Object.entries(buildFilterParams(filters)).forEach(([k, v]) =>
      url.searchParams.set(k, v)
    );

    let body: FormData | undefined;
    const headers: HeadersInit = {};

    if (imageFile) {
      body = new FormData();
      body.append("image", imageFile, "image.jpg");
    }

    const res = await fetch(`${base}/search${url.search}`, {
      method: "POST",
      body,
      headers,
      cache: "no-store",
    });

    if (!res.ok) return { total: 0, items: [] };
    return res.json();
  } catch {
    return { total: 0, items: [] };
  }
}

export async function registerCatalog(file: File): Promise<{
  status: string;
  stats?: Record<string, number>;
  detail?: string;
} | null> {
  try {
    const base = getApiBase();
    const form = new FormData();
    form.append("file", file, file.name);
    const res = await fetch(`${base}/catalog/register`, {
      method: "POST",
      body: form,
      cache: "no-store",
    });
    return res.json();
  } catch {
    return null;
  }
}

export function imageUrl(productId: number | string): string {
  // Always use the proxied path so it works in any environment
  return `/api/static/images/${productId}.jpg`;
}
