import type { NavItem } from "./index.ts";

export type VisitorResult = undefined | "break";

export function visit<T extends { children: T[] }>(
  items: readonly T[],
  visitor: (item: T, parents: readonly T[]) => VisitorResult,
): void {
  function visitItems(
    items: readonly T[],
    parents: readonly T[],
  ): VisitorResult {
    for (const item of items) {
      if (visitor(item, parents) === "break") {
        return "break";
      }
      if (visitItems(item.children, [...parents, item]) === "break") {
        return "break";
      }
    }
    return;
  }
  visitItems(items, []);
}

export function visitNavItems(
  navItems: readonly NavItem[],
  visitor: (navItem: NavItem, parents: readonly NavItem[]) => VisitorResult,
): void {
  function visitItems(
    navItems: readonly NavItem[],
    parents: readonly NavItem[],
  ): VisitorResult {
    for (const navItem of navItems) {
      if (visitor(navItem, parents) === "break") {
        return "break";
      }
      if (
        "items" in navItem &&
        visitItems(navItem.items, [...parents, navItem]) === "break"
      ) {
        return "break";
      }
    }
    return;
  }
  visitItems(navItems, []);
}
