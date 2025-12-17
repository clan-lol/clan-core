import { onClickOutside } from "./src/util";

export {};

export type ProcessMessage = {
  topic: string;
  data: unknown;
  origin: string;
};

declare global {
  interface Window {
    notifyBus: (data: ProcessMessage) => void;
  }
}
declare module "solid-js" {
  namespace JSX {
    interface DirectiveFunctions {
      onClickOutside: typeof onClickOutside;
    }
  }
}
