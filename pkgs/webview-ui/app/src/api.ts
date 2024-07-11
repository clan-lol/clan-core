import { FromSchema } from "json-schema-to-ts";
import { schema } from "@/api";
import { nanoid } from "nanoid";

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
  [K in OperationNames]: Record<
    string,
    (response: OperationResponse<K>) => void
  >;
};
const registry: ObserverRegistry = operationNames.reduce(
  (acc, opName) => ({
    ...acc,
    [opName]: {},
  }),
  {} as ObserverRegistry
);

function createFunctions<K extends OperationNames>(
  operationName: K
): {
  dispatch: (args: OperationArgs<K>) => void;
  receive: (fn: (response: OperationResponse<K>) => void, id: string) => void;
} {
  return {
    dispatch: (args: OperationArgs<K>) => {
      // Send the data to the gtk app
      window.webkit.messageHandlers.gtk.postMessage({
        method: operationName,
        data: args,
      });
    },
    receive: (fn: (response: OperationResponse<K>) => void, id: string) => {
      // @ts-expect-error: This should work although typescript doesn't let us write
      registry[operationName][id] = fn;

      window.clan[operationName] = (s: string) => {
        const f = (response: OperationResponse<K>) => {
          if (response.op_key === id) {
            registry[operationName][id](response);
          }
        };
        deserialize(f)(s);
      };
    },
  };
}

type PyApi = {
  [K in OperationNames]: {
    dispatch: (args: OperationArgs<K>) => void;
    receive: (fn: (response: OperationResponse<K>) => void, id: string) => void;
  };
};

function download(filename: string, text: string) {
  const element = document.createElement("a");
  element.setAttribute(
    "href",
    "data:text/plain;charset=utf-8," + encodeURIComponent(text)
  );
  element.setAttribute("download", filename);

  element.style.display = "none";
  document.body.appendChild(element);

  element.click();

  document.body.removeChild(element);
}

export const callApi = <K extends OperationNames>(
  method: K,
  args: OperationArgs<K>
) => {
  return new Promise<OperationResponse<K>>((resolve, reject) => {
    const id = nanoid();
    pyApi[method].receive((response) => {
      if (response.status === "error") {
        reject(response);
      }
      resolve(response);
    }, id);

    pyApi[method].dispatch({ ...args, op_key: id });
  });
};

const deserialize =
  <T>(fn: (response: T) => void) =>
  (str: string) => {
    try {
      fn(JSON.parse(str) as T);
    } catch (e) {
      console.log("Error parsing JSON: ", e);
      console.log({ download: () => download("error.json", str) });
      console.error(str);
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
