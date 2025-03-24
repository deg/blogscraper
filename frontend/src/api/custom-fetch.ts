// src/api/custom-fetch.ts
export const customFetch = async ({ url, method, options }) => {
  const response = await fetch(`${url}`, {
    method,
    ...options,
  })
  return response.json()
}
