import { config } from "@/models";
import { Methods, Body, Header, Response, SuccessResponse } from "./client";

async function call<Method extends Methods>(
  method: Method,
  {
    body,
    header,
    signal,
  }: {
    body?: Body<Method> | undefined;
    header?: Header | undefined;
    signal?: AbortSignal | undefined;
  } = {},
): Promise<SuccessResponse<Method>> {
  const taskId = window.crypto.randomUUID();
  let isDone = false;
  signal?.addEventListener("abort", () => {
    if (isDone) return;
    void (async () => {
      await call("delete_task", { body: { task_id: taskId } });
    })();
  });

  const result = await fetch(`${config.clanAPIBase}/api/v1/${method}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    signal,
    body: JSON.stringify({
      body,
      header: {
        ...header,
        op_key: taskId,
      },
    }),
  });
  const res = (await result.json()) as {
    body: Response<Method>;
    header: Record<string, unknown>;
  };
  isDone = true;

  if (res.body.status == "error") {
    const err = res.body.errors[0];
    if (err) {
      throw new Error(`${err.message}: ${err.description}`);
    }
  }

  return res.body as SuccessResponse<Method>;
}

export default { call };
