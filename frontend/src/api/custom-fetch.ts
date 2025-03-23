// src/api/custom-fetch.ts
export const customFetch = async ({ url, options }) => {
  const response = await fetch(`http://localhost:8000${url}`, options)
  return response.json()
}
