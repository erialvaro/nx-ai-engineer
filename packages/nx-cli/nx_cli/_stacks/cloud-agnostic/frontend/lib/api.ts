// Backend access via environment only (NEXT_PUBLIC_API_URL) — cloud-agnostic.
// The browser bundle reads the value baked at build/runtime; no provider SDK.

export function getApiUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:{{backend_port}}';
}

export async function getHealth(): Promise<{ status: string }> {
  const res = await fetch(getApiUrl() + '/health', { cache: 'no-store' });
  if (!res.ok) throw new Error('backend unhealthy');
  return res.json();
}
