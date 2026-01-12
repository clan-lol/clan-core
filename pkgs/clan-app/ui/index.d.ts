import { onClickOutside } from "./src/util";

export {};

export type ProcessMessage = {
  topic: string;
  data: unknown;
  origin: string;
};

declare global {
  /* eslint-disable-next-line @typescript-eslint/consistent-type-definitions */
  interface Window {
    notifyBus: (data: ProcessMessage) => void;
  }
}
declare module "solid-js" {
  namespace JSX {
    /* eslint-disable-next-line @typescript-eslint/consistent-type-definitions */
    interface DirectiveFunctions {
      onClickOutside: typeof onClickOutside;
    }
  }
}
