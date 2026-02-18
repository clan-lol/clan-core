export type VisitorResult = void | "break";

export function visit<
  T extends object & {
    children?: readonly T[];
  },
>(
  items: readonly T[],
  visitor: (
    item: T,
    index: number,
    parents: readonly {
      index: number;
      value: Extract<T, { children: readonly T[] }>;
    }[],
  ) => VisitorResult,
): void {
  function visitItems(
    items: readonly T[],
    parents: readonly {
      index: number;
      value: Extract<T, { children: readonly T[] }>;
    }[],
  ): VisitorResult {
    for (const [i, item] of items.entries()) {
      if (visitor(item, i, parents) === "break") {
        return "break";
      }
      if (!item.children) {
        continue;
      }
      if (
        visitItems(item.children, [
          ...parents,
          {
            index: i,
            value: item as Extract<T, { children: readonly T[] }>,
          },
        ]) === "break"
      ) {
        return "break";
      }
    }
  }
  visitItems(items, []);
}
