import { createStore, SetStoreFunction } from "solid-js/store";
import { ToolbarMode, ToolbarMethods, createToolbarMethods } from "./toolbar";
import { createModalMethods, Modal, ModalMethods } from "./modal";

export * from "./Context";
export type { ToolbarMode, ToolbarMethods, Modal, ModalMethods };

export type UI = {
  toolbarMode: ToolbarMode;
  modal: Modal | null;
};

export function createUIStore(): readonly [UI, UIMethods] {
  const [ui, setUI] = createStore<UI>({
    toolbarMode: { type: "select" },
    modal: null,
  });

  return [ui, createUIMethods(ui, setUI)];
}

export type UIMethods = ToolbarMethods & ModalMethods;

export function createUIMethods(
  ui: UI,
  setUI: SetStoreFunction<UI>,
): UIMethods {
  const self: UIMethods = {
    ...createToolbarMethods(ui, setUI),
    ...createModalMethods(ui, setUI),
  };
  return self;
}
