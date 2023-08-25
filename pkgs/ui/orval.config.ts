const config = {
  petstore: {
    output: {
      mode: "tags-split",
      target: "api",
      schemas: "api/model",
      client: "swr",
      // mock: true,
    },
    input: {
      target: "./openapi.json",
    },
  },
};

export default config;
