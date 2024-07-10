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
  const { op_key } = data;
  if (method === "open_file") {
    return {
      status: "success",
      data: "/home/johannes/git/clan-core",
      op_key,
    };
  }

  // @ts-expect-error: fakeData is guaranteed to always be some object
  return { ...fakeData, op_key };
};

export { getFakeResponse };
