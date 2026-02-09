export type VisitorResult = void | "break";

type Nesting<T, ChildrenKey extends string> = T &
  Partial<Record<ChildrenKey, readonly Nesting<T, ChildrenKey>[]>>;
type Parent<T, ChildrenKey extends string> = T &
  Record<ChildrenKey, readonly Nesting<T, ChildrenKey>[]>;

export function visit<T extends object, ChildrenKey extends string>(
  items: readonly Nesting<T, ChildrenKey>[],
  childrenKey: ChildrenKey,
  visitor: (
    item: T,
    parents: readonly Parent<T, ChildrenKey>[],
  ) => VisitorResult,
): void {
  function visitItems(
    items: readonly Nesting<T, ChildrenKey>[],
    parents: readonly Parent<T, ChildrenKey>[],
  ): VisitorResult {
    for (const item of items) {
      if (visitor(item, parents) === "break") {
        return "break";
      }
      if (
        childrenKey in item &&
        visitItems(item[childrenKey] as T[], [
          ...parents,
          item as Parent<T, ChildrenKey>,
        ]) === "break"
      ) {
        return "break";
      }
    }
    return;
  }
  visitItems(items, []);
}
