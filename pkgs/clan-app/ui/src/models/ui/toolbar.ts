import { produce, SetStoreFunction } from "solid-js/store";
import { Service, ServiceInstance, UI } from "..";

export type ToolbarMode =
  | { type: "select" }
  | { type: "create" }
  | { type: "move" }
  | {
      type: "service";
      subtype?: undefined;
    }
  | ToolbarServiceInstanceMode;
export type ToolbarServiceInstanceMode =
  | {
      type: "service";
      subtype: "create";
      service: Service;
      highlighting?: boolean;
    }
  | {
      type: "service";
      subtype: "edit";
      serviceInstance: ServiceInstance;
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
