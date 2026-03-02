export function mapObjectValues<T, U>(
  o: Record<string, T>,
  fn: (v: [string, T], i: number, arr: [string, T][]) => U,
): Record<string, U> {
  return Object.fromEntries(
    Object.entries(o).map((item, i, arr) => [item[0], fn(item, i, arr)]),
  );
}
export async function asyncMapObjectValues<T, U>(
  o: Record<string, T>,
  fn: (v: [string, T], i: number, arr: [string, T][]) => Promise<U>,
): Promise<Record<string, U>> {
  return Object.fromEntries(
    await Promise.all(
      Object.entries(o).map(
        async (item, i, arr) => [item[0], await fn(item, i, arr)] as const,
      ),
    ),
  );
}

export function mapObjectKeys<T>(
  o: Record<string, T>,
  fn: (v: [string, T], i: number, arr: [string, T][]) => string,
): Record<string, T> {
  return Object.fromEntries(
    Object.entries(o).map((item, i, arr) => [fn(item, i, arr), item[1]]),
  );
}
export function mapObjectKeyValues<T, U>(
  o: Record<string, T>,
  fn: (v: [string, T], i: number, arr: [string, T][]) => [string, U],
): Record<string, U> {
  return Object.fromEntries(
    Object.entries(o).map((item, i, arr) => fn(item, i, arr)),
  );
}
export async function asyncMapObjectKeyValues<T, U>(
  o: Record<string, T>,
  fn: (
    v: [string, T],
    i: number,
    arr: [string, T][],
  ) => Promise<readonly [string, U]>,
): Promise<Record<string, U>> {
  return Object.fromEntries(
    await Promise.all(
      Object.entries(o).map(async (item, i, arr) => await fn(item, i, arr)),
    ),
  );
}
