import { API } from "@/api/API";
import { Schema as Inventory } from "@/api/Inventory";

export type OperationNames = keyof API;
type Services = NonNullable<Inventory["services"]>;
type ServiceNames = keyof Services;

export type OperationArgs<T extends OperationNames> = API[T]["arguments"];
export type OperationResponse<T extends OperationNames> = API[T]["return"];

export type ClanServiceInstance<T extends ServiceNames> = NonNullable<
  Services[T]
>[string];

export type SuccessQuery<T extends OperationNames> = Extract<
  OperationResponse<T>,
  { status: "success" }
>;
export type SuccessData<T extends OperationNames> = SuccessQuery<T>["data"];

interface SendHeaderType {
  logging?: { group_path: string[] };
  op_key?: string;
}
interface BackendSendType<K extends OperationNames> {
  body: OperationArgs<K>;
  header?: SendHeaderType;
}

// eslint-disable-next-line @typescript-eslint/no-empty-object-type
interface ReceiveHeaderType {}
interface BackendReturnType<K extends OperationNames> {
  body: OperationResponse<K>;
  header: ReceiveHeaderType;
}

/**
 * Interface representing an API call with a unique identifier, result promise, and cancellation capability.
 *
 * @template K - A generic type parameter extending the set of operation names.
 *
 * @property {string} uuid - A unique identifier for the API call.
 * @property {Promise<BackendReturnType<K>>} result - A promise that resolves to the return type of the backend operation.
 * @property {() => Promise<void>} cancel - A function to cancel the API call, returning a promise that resolves when cancellation is completed.
 */
export interface ApiCall<K extends OperationNames> {
  uuid: string;
  result: Promise<OperationResponse<K>>;
  cancel: () => Promise<void>;
}

/**
 * Do not use this function directly, use `useApiClient` function instead.
 * This allows mocking the result in tests.
 * Or switch to different client implementations.
 */
export const callApi = <K extends OperationNames>(
  method: K,
  args: OperationArgs<K>,
  backendOpts?: SendHeaderType,
): ApiCall<K> => {
  // if window[method] does not exist, throw an error
  if (!(method in window)) {
    console.error(`Method ${method} not found on window object`);

    return {
      uuid: "",
      result: Promise.reject(`Method ${method} not found on window object`),
      cancel: () => Promise.resolve(),
    };
  }

  const op_key = backendOpts?.op_key ?? crypto.randomUUID();

  const req: BackendSendType<OperationNames> = {
    body: args,
    header: {
      ...backendOpts,
      op_key,
    },
  };

  const result = (
    window as unknown as Record<
      OperationNames,
      (
        args: BackendSendType<OperationNames>,
      ) => Promise<BackendReturnType<OperationNames>>
    >
  )[method](req) as Promise<BackendReturnType<K>>;

  return {
    uuid: op_key,
    result: result.then(({ body }) => body),
    cancel: async () => {
      console.log("Cancelling api call: ", op_key);
      await callApi("delete_task", { task_id: op_key }).result;
    },
  };
};
