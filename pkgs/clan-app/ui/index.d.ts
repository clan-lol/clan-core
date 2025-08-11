import { ProcessMessage } from "./src/hooks/notify";

export {};

declare global {
  interface Window {
    notifyBus: (data: ProcessMessage) => void;
  }
}
