import type { NavItem } from ".";

export type VisitorResult = undefined | "break";

export function visit<T extends { children: T[] }>(
  items: T[],
  visitor: (item: T, parents: T[]) => VisitorResult,
): void {
  function visitItems(items: T[], parents: T[]): VisitorResult {
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
  navItems: NavItem[],
  visitor: (navItem: NavItem, parents: NavItem[]) => VisitorResult,
): void {
  function visitItems(navItems: NavItem[], parents: NavItem[]): VisitorResult {
    for (const navItem of navItems) {
      if (visitor(navItem, parents) === "break") {
        return "break";
      }
      if ("items" in navItem) {
        if (visitItems(navItem.items, [...parents, navItem]) === "break") {
          return "break";
        }
      }
    }
    return;
  }
  visitItems(navItems, []);
}
