import { JSONSchemaFaker } from "json-schema-faker";
import { schema } from "./api/index";
import { OperationNames } from "./src/api";

const faker = JSONSchemaFaker;

faker.option({
  alwaysFakeOptionals: true,
});

const getFakeResponse = (method: OperationNames, data: any) => {
  const fakeData = faker.generate(schema.properties[method].properties.return);
  return fakeData;
};

export { getFakeResponse };
