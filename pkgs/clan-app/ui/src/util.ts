export const pick = <T, K extends keyof T>(obj: T, keys: K[]): Pick<T, K> =>
  keys.reduce(
    (acc, key) => {
      acc[key] = obj[key];
      return acc;
    },
    {} as Pick<T, K>,
  );

export const removeEmptyStrings = <T>(obj: T): T => {
  if (obj === null || obj === undefined) {
    return obj;
  }

  if (typeof obj === "string") {
    return obj;
  }

  if (Array.isArray(obj)) {
    return obj.map((item) => removeEmptyStrings(item)) as T;
  }

  if (typeof obj === "object") {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const result: any = {};
    for (const key in obj) {
      // eslint-disable-next-line no-prototype-builtins
      if (obj.hasOwnProperty(key)) {
        const value = obj[key];
        if (value !== "") {
          result[key] = removeEmptyStrings(value);
        }
      }
    }

    return result;
  }

  return obj;
};

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
export const getInClasses = <T extends Record<string, string>, U>(
  styles: T,
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
