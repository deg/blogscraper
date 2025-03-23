// src/api/custom-fetch.ts
export const customFetch = async ({ url, method, options }) => {
  const response = await fetch(`http://localhost:8000${url}`, {
    method,
    ...options,
  })
  return response.json()
}
