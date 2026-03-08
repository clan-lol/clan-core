export async function sleep(
  n: number,
  { signal }: { signal?: AbortSignal } = {},
): Promise<void> {
  const { resolve, reject, promise } = Promise.withResolvers();
  const id = setTimeout(resolve, n);
  signal?.addEventListener("abort", () => {
    clearTimeout(id);
    reject(signal.reason);
  });
  await promise;
}
