import { API } from "@/api/API";

type Methods = keyof API;
interface Header {
  logging?: { group_path: string[] };
  op_key?: string;
}
type Body<Method extends Methods> = API[Method]["arguments"];
type Response<Method extends Methods> = API[Method]["return"];
type SuccessResponse<Method extends Methods> = Extract<
  Response<Method>,
  { status: "success" }
>;
async function call<Method extends Methods>(
  method: Method,
  {
    body,
    header,
    signal,
  }: {
    body?: Body<Method>;
    header?: Header;
    signal?: AbortSignal;
  } = {},
): Promise<SuccessResponse<Method>> {
  const fn = (
    window as unknown as Record<
      Method,
      (args: { body?: Body<Method>; header?: Header }) => Promise<{
        body: Response<Method>;
        header: Record<string, unknown>;
      }>
    >
  )[method];
  if (typeof fn != "function") {
    throw new Error(`Cannot call clan non-existant method: ${method}`);
  }

  const taskId = window.crypto.randomUUID();
  let isDone = false;
  signal?.addEventListener("abort", async () => {
    if (isDone) return;
    await call("delete_task", { body: { task_id: taskId } });
  });

  const res = await fn({
    body,
    header: {
      ...header,
      op_key: taskId,
    },
  });
  isDone = true;

  if (res.body.status == "error") {
    const err = res.body.errors[0];
    throw new Error(`${err.message}: ${err.description}`);
  }

  return res.body as SuccessResponse<Method>;
}

export default {
  async get<Method extends Methods>(
    url: Method,
    { signal }: { signal?: AbortSignal } = {},
  ) {
    return await call(url, { signal });
  },
  async post<Method extends Methods>(
    url: Method,
    { signal, body }: { signal?: AbortSignal; body: Body<Method> },
  ) {
    return await call(url, { signal, body });
  },
};
