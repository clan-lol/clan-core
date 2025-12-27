import { Accessor, onCleanup } from "solid-js";

// Join truthy values with dashes
// joinByDash("button", "", false, null, "x")'s return type is "button-x"
export const joinByDash = <
  T extends readonly (string | null | undefined | false)[],
>(
  ...args: T
): DashJoined<FilterFalsy<T>> => {
  return keepTruthy(...args).join("-") as DashJoined<FilterFalsy<T>>;
};

// Turn a component's "in" attribute value to a list of css module class names
export const getInClasses = <U extends string>(
  styles: Record<string, string>,
  localIn?: U | U[],
): string[] => {
  if (!localIn) {
    return [""];
  }
  let localIns: U[];
  if (!Array.isArray(localIn)) {
    localIns = [localIn];
  } else {
    localIns = localIn;
  }
  return localIns.map((localIn) => styles[`in-${localIn}`]);
};

export const keepTruthy = <T>(...items: T[]): FilterFalsy<T[]> =>
  items.filter(Boolean) as FilterFalsy<T[]>;

type FilterFalsy<T extends readonly unknown[]> = T extends readonly [
  infer Head,
  ...infer Tail,
]
  ? Head extends "" | null | undefined | false
    ? FilterFalsy<Tail>
    : [Head, ...FilterFalsy<Tail>]
  : [];

type DashJoined<T extends readonly string[]> = T extends readonly [infer First]
  ? First
  : T extends readonly [infer First, ...infer Rest]
    ? First extends string
      ? Rest extends readonly string[]
        ? `${First}-${DashJoined<Rest>}`
        : never
      : never
    : "";

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
export function isPosition(
  a: readonly [number, number],
  b: readonly [number, number],
) {
  return a[0] === b[0] && a[1] === b[1];
}

export function onClickOutside(
  el: HTMLElement,
  value: Accessor<() => void>,
): void {
  const listener = (ev: MouseEvent) => {
    if (!el.contains(ev.target as Node)) {
      const fn = value();
      fn();
    }
  };
  document.addEventListener("mousedown", listener);
  onCleanup(() => document.removeEventListener("mousedown", listener));
}
