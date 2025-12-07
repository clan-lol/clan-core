// highlightStore.ts
import { createStore, produce } from "solid-js/store";

// groups: { [groupName: string]: Set<nodeId> }
const [highlightGroups, setHighlightGroups] = createStore<
  Record<string, Set<string>>
>({});

// Add highlight
function highlight(group: string, nodeId: string) {
  setHighlightGroups(group, (prev = new Set()) => {
    const next = new Set(prev);
    next.add(nodeId);
    return next;
  });
}

// Remove highlight
function unhighlight(group: string, nodeId: string) {
  setHighlightGroups(group, (prev = new Set()) => {
    const next = new Set(prev);
    next.delete(nodeId);
    return next;
  });
}

// Clear group
export function clearHighlight(group: string) {
  setHighlightGroups(group, () => new Set());
}

export function clearAllHighlights() {
  setHighlightGroups(
    produce((s) => {
      for (const key of Object.keys(s)) {
        Reflect.deleteProperty(s, key);
      }
    }),
  );
}

export { highlightGroups, setHighlightGroups };
