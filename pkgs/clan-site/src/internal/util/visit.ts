export type VisitorResult = undefined | "break";

type Nesting<T, K extends string> = T &
  Partial<Record<K, readonly Nesting<T, K>[]>>;
export function visit<ChildrenKey extends string, T extends object>(
  items: readonly Nesting<T, ChildrenKey>[],
  childrenKey: ChildrenKey,
  visitor: (item: T, parents: readonly T[]) => VisitorResult,
): void {
  function visitItems(
    items: readonly Nesting<T, ChildrenKey>[],
    parents: readonly Nesting<T, ChildrenKey>[],
  ): VisitorResult {
    for (const item of items) {
      if (visitor(item, parents) === "break") {
        return "break";
      }
      if (
        childrenKey in item &&
        visitItems(item[childrenKey] as T[], [...parents, item]) === "break"
      ) {
        return "break";
      }
    }
    return;
  }
  visitItems(items, []);
}
