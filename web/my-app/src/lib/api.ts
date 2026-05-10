export const getApiUrl = () => {
  // server
  if (typeof window === 'undefined') {
    return process.env.INTERNAL_API_URL || "http://server:8000";
  }

  // browser
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
};

export async function apiFetch(endpoint: string, options: RequestInit = {}) {
  const baseUrl = getApiUrl();
  const url = `${baseUrl}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
  
  return fetch(url, options);
}