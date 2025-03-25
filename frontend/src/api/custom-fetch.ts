// src/api/custom-fetch.ts

export const customFetch = async ({ url, method, params, options }) => {
  const queryString =
    params && Object.keys(params).length > 0
      ? `?${new URLSearchParams(params).toString()}`
      : ""

  const response = await fetch(`${url}${queryString}`, {
    method,
    ...options,
  })

  return response.json()
}
