import { ProcessMessage } from "./src/hooks/api";

export {};

declare global {
  interface Window {
    notifyBus: (data: ProcessMessage) => void;
  }
}
