import { FromSchema } from "json-schema-to-ts";
import { schema } from "@/api";

type API = FromSchema<typeof schema>;

type OperationNames = keyof API;
type OperationArgs<T extends OperationNames> = API[T]["argument"];
type OperationResponse<T extends OperationNames> = API[T]["return"];

declare global {
  interface Window {
    clan: {
      [K in OperationNames]: (str: string) => void;
    };
    webkit: {
      messageHandlers: {
        gtk: {
          postMessage: (message: { method: OperationNames; data: any }) => void;
        };
      };
    };
  }
}

function createFunctions<K extends OperationNames>(
  operationName: K
): {
  dispatch: (args: OperationArgs<K>) => void;
  receive: (fn: (response: OperationResponse<K>) => void) => void;
} {
  return {
    dispatch: (args: OperationArgs<K>) => {
      console.log(
        `Operation: ${operationName}, Arguments: ${JSON.stringify(args)}`
      );
      // Send the data to the gtk app
      window.webkit.messageHandlers.gtk.postMessage({
        method: operationName,
        data: args,
      });
    },
    receive: (fn: (response: OperationResponse<K>) => void) => {
      window.clan.list_machines = deserialize(fn);
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
      fn(JSON.parse(str) as T);
    } catch (e) {
      alert(`Error parsing JSON: ${e}`);
    }
  };

// Create the API object

const pyApi: PyApi = {} as PyApi;
operationNames.forEach((name) => {
  pyApi[name] = createFunctions(name);
});
export { pyApi };
