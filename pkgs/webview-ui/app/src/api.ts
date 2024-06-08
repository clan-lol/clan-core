import { FromSchema } from "json-schema-to-ts";
import { schema } from "@/api";

export type API = FromSchema<typeof schema>;

export type OperationNames = keyof API;
export type OperationArgs<T extends OperationNames> = API[T]["arguments"];
export type OperationResponse<T extends OperationNames> = API[T]["return"];

export type SuccessData<T extends OperationNames> = Extract<
  OperationResponse<T>,
  { status: "success" }
>;

export type ClanOperations = {
  [K in OperationNames]: (str: string) => void;
};
declare global {
  interface Window {
    clan: ClanOperations;
    webkit: {
      messageHandlers: {
        gtk: {
          postMessage: (message: {
            method: OperationNames;
            data: OperationArgs<OperationNames>;
          }) => void;
        };
      };
    };
  }
}
// Make sure window.webkit is defined although the type is not correctly filled yet.
window.clan = {} as ClanOperations;

function createFunctions<K extends OperationNames>(
  operationName: K
): {
  dispatch: (args: OperationArgs<K>) => void;
  receive: (fn: (response: OperationResponse<K>) => void) => void;
} {
  return {
    dispatch: (args: OperationArgs<K>) => {
      console.log(
        `Operation: ${String(operationName)}, Arguments: ${JSON.stringify(args)}`
      );
      // Send the data to the gtk app
      window.webkit.messageHandlers.gtk.postMessage({
        method: operationName,
        data: args,
      });
    },
    receive: (fn: (response: OperationResponse<K>) => void) => {
      window.clan[operationName] = deserialize(fn);
    },
  };
}

const operations = schema.properties;
const operationNames = Object.keys(operations) as OperationNames[];

type PyApi = {
  [K in OperationNames]: {
    dispatch: (args: OperationArgs<K>) => void;
    receive: (fn: (response: OperationResponse<K>) => void) => void;
  };
};

const deserialize =
  <T>(fn: (response: T) => void) =>
  (str: string) => {
    try {
      console.debug("Received data: ", str);
      fn(JSON.parse(str) as T);
    } catch (e) {
      alert(`Error parsing JSON: ${e}`);
    }
  };

// Create the API object

const pyApi: PyApi = {} as PyApi;

operationNames.forEach((opName) => {
  const name = opName as OperationNames;
  // @ts-expect-error - TODO: Fix this. Typescript is not recognizing the receive function correctly
  pyApi[name] = createFunctions(name);
});

pyApi.open_file.receive((r) => {
  const { status } = r;
  if (status === "error") return console.error(r.errors);
  console.log(r.data);
  alert(r.data);
});

export { pyApi };
