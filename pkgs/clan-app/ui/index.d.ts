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
