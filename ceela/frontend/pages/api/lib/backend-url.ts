/**
 * Obtiene la URL del backend según el contexto:
 * - Server-side (Next.js API routes): usa BACKEND_URL (http://app:8000)
 * - Client-side (navegador): usa NEXT_PUBLIC_API_ENDPOINT (http://localhost:18000)
 */
export function getBackendUrl(): string {
  // En server-side (Next.js API routes), usar BACKEND_URL
  if (typeof window === 'undefined') {
    return process.env.BACKEND_URL || 'http://app:8000';
  }

  // En client-side, usar NEXT_PUBLIC_API_ENDPOINT
  return process.env.NEXT_PUBLIC_API_ENDPOINT || 'http://localhost:18000';
}
