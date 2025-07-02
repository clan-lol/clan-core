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

function isMachine(obj: unknown): obj is Machine {
  return (
    !!obj &&
    typeof obj === "object" &&
    typeof (obj as any).name === "string" &&
    typeof (obj as any).flake === "object" &&
    typeof (obj as any).flake.identifier === "string"
  );
}

// Machine type with flake for API calls
interface Machine {
  name: string;
  flake: {
    identifier: string;
  };
}

interface BackendOpts {
  logging?: { group: string | Machine };
}

interface BackendReturnType<K extends OperationNames> {
  body: OperationResponse<K>;
  header: Record<string, any>;
}

const _callApi = <K extends OperationNames>(
  method: K,
  args: OperationArgs<K>,
  backendOpts?: BackendOpts,
): { promise: Promise<BackendReturnType<K>>; op_key: string } => {
  // if window[method] does not exist, throw an error
  if (!(method in window)) {
    console.error(`Method ${method} not found on window object`);
    // return a rejected promise
    return {
      promise: Promise.resolve({
        body: {
          status: "error",
          errors: [
            {
              message: `Method ${method} not found on window object`,
              code: "method_not_found",
            },
          ],
          op_key: "noop",
        },
        header: {},
      }),
      op_key: "noop",
    };
  }

  let header: BackendOpts = {};
  if (backendOpts != undefined) {
    header = { ...backendOpts };
    let group = backendOpts?.logging?.group;
    if (group != undefined && isMachine(group)) {
      header = {
        logging: { group: group.flake.identifier + "#" + group.name },
      };
    }
  }

  const promise = (
    window as unknown as Record<
      OperationNames,
      (
        args: OperationArgs<OperationNames>,
        metadata: BackendOpts,
      ) => Promise<BackendReturnType<OperationNames>>
    >
  )[method](args, header) as Promise<BackendReturnType<K>>;

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const op_key = (promise as any)._webviewMessageId as string;

  return { promise, op_key };
};

const handleCancel = async <K extends OperationNames>(
  ops_key: string,
  orig_task: Promise<BackendReturnType<K>>,
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

  if (resp.body.status === "error") {
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
  backendOpts?: BackendOpts,
): { promise: Promise<OperationResponse<K>>; op_key: string } => {
  console.log("Calling API", method, args, backendOpts);

  const { promise, op_key } = _callApi(method, args, backendOpts);
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

    const body = response.body;
    if (body.status === "error" && !cancelled) {
      toast.remove(toastId);
      toast.custom(
        (t) => (
          <ErrorToastComponent
            t={t}
            message={"Error: " + body.errors[0].message}
          />
        ),
        {
          duration: Infinity,
        },
      );
    } else {
      toast.remove(toastId);
    }
    return body;
  });

  return { promise: new_promise, op_key: op_key };
};
