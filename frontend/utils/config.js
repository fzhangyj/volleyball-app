// H5 can use a same-origin /api/v1 proxy. For a separate backend or a native/
// mini-program build, set VITE_API_ORIGIN in frontend/.env before building.
export const API_ORIGIN = (import.meta.env.VITE_API_ORIGIN || '').trim().replace(/\/+$/, '')
export const BASE_URL = `${API_ORIGIN}/api/v1`

export function resolveMediaUrl(path) {
	if (!path) return ''
	return path.startsWith('/') ? `${API_ORIGIN}${path}` : path
}
