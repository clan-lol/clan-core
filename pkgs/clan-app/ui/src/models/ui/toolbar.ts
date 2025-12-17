import { produce, SetStoreFunction } from "solid-js/store";
import { Service, UI } from "..";

export type ToolbarMode =
  | { type: "select" }
  | { type: "create" }
  | { type: "move" }
  | {
      type: "service";
      service?: Service;
      highlighting?: boolean;
    };

export type ToolbarMethods = {
  setToolbarMode(mode: ToolbarMode): void;
};

export function createToolbarMethods(
  ui: UI,
  setUI: SetStoreFunction<UI>,
): ToolbarMethods {
  const self: ToolbarMethods = {
    setToolbarMode(mode) {
      setUI(
        produce((ui) => {
          ui.toolbarMode = mode;
        }),
      );
    },
  };
  return self;
}
