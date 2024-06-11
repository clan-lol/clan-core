import { JSONSchemaFaker } from "json-schema-faker";
import { schema } from "./api/index";
import { OperationNames } from "./src/api";

const faker = JSONSchemaFaker;

faker.option({
  alwaysFakeOptionals: true,
  useExamplesValue: true,
});

const getFakeResponse = (method: OperationNames, data: any) => {
  const fakeData = faker.generate(schema.properties[method].properties.return);

  if (method === "open_file") {
    return {
      status: "success",
      data: "/path/to/clan",
    };
  }

  return fakeData;
};

export { getFakeResponse };
