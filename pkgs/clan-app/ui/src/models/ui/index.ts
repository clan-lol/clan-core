import { createStore, produce, SetStoreFunction } from "solid-js/store";
import { Service, ServiceInstance } from "..";

export * from "./Context";

export type UI = {
  toolbarMode: ToolbarMode;
};
export type ToolbarMode =
  | { type: "select" }
  | { type: "create" }
  | { type: "move" }
  | ToolbarServiceMode;
export type ToolbarServiceMode =
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

export function createUIStore(): readonly [UI, UIMethods] {
  const [ui, setUI] = createStore<UI>({
    toolbarMode: { type: "select" },
  });
  return [ui, uiMethods([ui, setUI])];
}

export type UIMethods = {
  setToolbarMode(mode: ToolbarMode): void;
};

function uiMethods([ui, setUI]: [UI, SetStoreFunction<UI>]): UIMethods {
  const self: UIMethods = {
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

// serviceInstance:
//                 instance ||
//                 createServiceInstance(
//                   {
//                     data: {
//                       name: service.id,
//                       roles: mapObjectValues(service.roles, ([roleId]) => ({
//                         id: roleId,
//                         settings: {},
//                         machines: [],
//                         tags: [],
//                       })),
//                     },
//                   },
//                   () => service,
//                 ),
