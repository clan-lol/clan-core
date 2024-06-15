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
export type ErrorData<T extends OperationNames> = Extract<
  OperationResponse<T>,
  { status: "error" }
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

const operations = schema.properties;
const operationNames = Object.keys(operations) as OperationNames[];

type ObserverRegistry = {
  [K in OperationNames]: ((response: OperationResponse<K>) => void)[];
};
const obs: ObserverRegistry = operationNames.reduce(
  (acc, opName) => ({
    ...acc,
    [opName]: [],
  }),
  {} as ObserverRegistry
);

interface ReceiveOptions {
  /**
   * Calls only the registered function that has the same key as used with dispatch
   *
   */
  fnKey: string;
}
function createFunctions<K extends OperationNames>(
  operationName: K
): {
  dispatch: (args: OperationArgs<K>) => void;
  receive: (fn: (response: OperationResponse<K>) => void) => void;
} {
  return {
    dispatch: (args: OperationArgs<K>) => {
      // console.log(
      //   `Operation: ${String(operationName)}, Arguments: ${JSON.stringify(args)}`
      // );
      // Send the data to the gtk app
      window.webkit.messageHandlers.gtk.postMessage({
        method: operationName,
        data: args,
      });
    },
    receive: (
      fn: (response: OperationResponse<K>) => void
      // options?: ReceiveOptions
    ) => {
      obs[operationName].push(fn);
      window.clan[operationName] = (s: string) => {
        obs[operationName].forEach((f) => deserialize(f)(s));
      };
    },
  };
}

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

operationNames.forEach((opName) => {
  const name = opName as OperationNames;
  // @ts-expect-error - TODO: Fix this. Typescript is not recognizing the receive function correctly
  pyApi[name] = createFunctions(name);
});

export { pyApi };
