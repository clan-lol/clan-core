import schema from "@/api/API.json" with { type: "json" };
import { API, Error } from "@/api/API";
import { nanoid } from "nanoid";
import { Schema as Inventory } from "@/api/Inventory";
import { toast, Toast } from "solid-toast";
import {
  ErrorToastComponent,
  CancelToastComponent,
} from "@/src/components/toast";
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

export type ClanOperations = Record<OperationNames, (str: string) => void>;

export interface GtkResponse<T> {
  result: T;
  op_key: string;
}
const _callApi = <K extends OperationNames>(
  method: K,
  args: OperationArgs<K>,
): { promise: Promise<OperationResponse<K>>; op_key: string } => {
  const promise = (
    window as unknown as Record<
      OperationNames,
      (
        args: OperationArgs<OperationNames>,
      ) => Promise<OperationResponse<OperationNames>>
    >
  )[method](args) as Promise<OperationResponse<K>>;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const op_key = (promise as any)._webviewMessageId as string;

  return { promise, op_key };
};

const handleCancel = async <K extends OperationNames>(
  ops_key: string,
  orig_task: Promise<OperationResponse<K>>,
) => {
  console.log("Canceling operation: ", ops_key);
  const { promise, op_key } = _callApi("cancel_task", { task_id: ops_key });
  const resp = await promise;

  if (resp.status === "error") {
    toast.custom(
      (t) => (
        <ErrorToastComponent
          t={t}
          message={"Failed to cancel operation: " + ops_key}
        />
      ),
      {
        duration: 5000,
      },
    );
  } else {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (orig_task as any).cancelled = true;
  }
  console.log("Cancel response: ", resp);
};

export const callApi = async <K extends OperationNames>(
  method: K,
  args: OperationArgs<K>,
): Promise<OperationResponse<K>> => {
  console.log("Calling API", method, args);
  const { promise, op_key } = _callApi(method, args);

  const toastId = toast.custom(
    (
      t, // t is the Toast object, t.id is the id of THIS toast instance
    ) => (
      <CancelToastComponent
        t={t}
        message={"Exectuting " + method}
        onCancel={handleCancel.bind(null, op_key, promise)}
      />
    ),
    {
      duration: Infinity,
    },
  );

  const response = await promise;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const cancelled = (promise as any).cancelled;
  if (cancelled) {
    console.log("Not printing toast because operation was cancelled");
  }

  if (response.status === "error" && !cancelled) {
    toast.remove(toastId);
    toast.custom(
      (t) => (
        <ErrorToastComponent
          t={t}
          message={"Error: " + response.errors[0].message}
        />
      ),
      {
        duration: Infinity,
      },
    );
  } else {
    toast.remove(toastId);
  }
  return response as OperationResponse<K>;
};
