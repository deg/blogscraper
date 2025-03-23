// openapi/orval.config.ts
export default {
  blogscraper: {
    input: './schema.json',
    output: {
      target: '../src/api/orval.ts',
      client: 'react-query',
      schemas: '../src/api/types',
      override: {
        mutator: {
          path: '../src/api/custom-fetch.ts',
          name: 'customFetch',
        },
      },
    },
    hooks: {
      transform: true,
    },
  },
}
