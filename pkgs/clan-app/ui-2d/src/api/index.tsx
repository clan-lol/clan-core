import { API } from "@/api/API";
import { Schema as Inventory } from "@/api/Inventory";
import { toast } from "solid-toast";
import {
  ErrorToastComponent,
  CancelToastComponent,
} from "@/src/components/toast";

type OperationNames = keyof API;
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

const _callApi = <K extends OperationNames>(
  method: K,
  args: OperationArgs<K>,
): { promise: Promise<OperationResponse<K>>; op_key: string } => {
  // if window[method] does not exist, throw an error
  if (!(method in window)) {
    console.error(`Method ${method} not found on window object`);
    // return a rejected promise
    return {
      promise: Promise.resolve({
        status: "error",
        errors: [
          {
            message: `Method ${method} not found on window object`,
            code: "method_not_found",
          },
        ],
        op_key: "noop",
      }),
      op_key: "noop",
    };
  }

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
  promise.catch((error) => {
    toast.custom(
      (t) => (
        <ErrorToastComponent
          t={t}
          message={"Unexpected error: " + (error?.message || String(error))}
        />
      ),
      {
        duration: 5000,
      },
    );
    console.error("Unhandled promise rejection in callApi:", error);
  });
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

export const callApi = <K extends OperationNames>(
  method: K,
  args: OperationArgs<K>,
): { promise: Promise<OperationResponse<K>>; op_key: string } => {
  console.log("Calling API", method, args);

  const { promise, op_key } = _callApi(method, args);
  promise.catch((error) => {
    toast.custom(
      (t) => (
        <ErrorToastComponent
          t={t}
          message={"Unexpected error: " + (error?.message || String(error))}
        />
      ),
      {
        duration: 5000,
      },
    );
    console.error("Unhandled promise rejection in callApi:", error);
  });

  const toastId = toast.custom(
    (
      t, // t is the Toast object, t.id is the id of THIS toast instance
    ) => (
      <CancelToastComponent
        t={t}
        message={"Executing " + method}
        onCancel={handleCancel.bind(null, op_key, promise)}
      />
    ),
    {
      duration: Infinity,
    },
  );

  const new_promise = promise.then((response) => {
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
    return response;
  });
  return { promise: new_promise, op_key: op_key };
};
