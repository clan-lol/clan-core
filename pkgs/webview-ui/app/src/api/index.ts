import schema from "@/api/API.json" assert { type: "json" };
import { API, Error } from "@/api/API";
import { nanoid } from "nanoid";
import { Schema as Inventory } from "@/api/Inventory";

export type OperationNames = keyof API;
export type OperationArgs<T extends OperationNames> = API[T]["arguments"];
export type OperationResponse<T extends OperationNames> = API[T]["return"];

export type ApiEnvelope<T> =
  | {
      status: "success";
      data: T;
      op_key: string;
    }
  | Error;

export type Services = NonNullable<Inventory["services"]>;
export type ServiceNames = keyof Services;
export type ClanService<T extends ServiceNames> = Services[T];
export type ClanServiceInstance<T extends ServiceNames> = NonNullable<
  Services[T]
>[string];

export type SuccessQuery<T extends OperationNames> = Extract<
  OperationResponse<T>,
  { status: "success" }
>;
export type SuccessData<T extends OperationNames> = SuccessQuery<T>["data"];

export type ErrorQuery<T extends OperationNames> = Extract<
  OperationResponse<T>,
  { status: "error" }
>;
export type ErrorData<T extends OperationNames> = ErrorQuery<T>["errors"];

export type ClanOperations = {
  [K in OperationNames]: (str: string) => void;
};

export interface GtkResponse<T> {
  result: T;
  op_key: string;
}

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
  {} as ObserverRegistry,
);

function createFunctions<K extends OperationNames>(
  operationName: K,
): {
  dispatch: (args: OperationArgs<K>) => void;
  receive: (fn: (response: OperationResponse<K>) => void, id: string) => void;
} {
  window.clan[operationName] = (s: string) => {
    const f = (response: OperationResponse<K>) => {
      // Get the correct receiver function for the op_key
      const receiver = registry[operationName][response.op_key];
      if (receiver) {
        receiver(response);
      }
    };
    deserialize(f)(s);
  };

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
    "data:text/plain;charset=utf-8," + encodeURIComponent(text),
  );
  element.setAttribute("download", filename);

  element.style.display = "none";
  document.body.appendChild(element);

  element.click();

  document.body.removeChild(element);
}

export const callApi = <K extends OperationNames>(
  method: K,
  args: OperationArgs<K>,
) => {
  return new Promise<OperationResponse<K>>((resolve) => {
    const id = nanoid();
    pyApi[method].receive((response) => {
      console.log(method, "Received response: ", { response });
      resolve(response);
    }, id);

    pyApi[method].dispatch({ ...args, op_key: id });
  });
};

const deserialize =
  <T>(fn: (response: T) => void) =>
  (r: unknown) => {
    try {
      fn(r as T);
    } catch (e) {
      console.error("Error parsing JSON: ", e);
      window.localStorage.setItem("error", JSON.stringify(r));
      console.error(r);
      console.error("See localStorage 'error'");
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
