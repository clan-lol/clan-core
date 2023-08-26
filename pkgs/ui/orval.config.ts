const config = {
  petstore: {
    output: {
      mode: "tags-split",
      target: "src/api",
      schemas: "src/api/model",
      client: "swr",
      // mock: true,
    },
    input: {
      target: "./openapi.json",
    },
  },
};

export default config;
