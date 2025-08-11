import { createSignal, onCleanup } from "solid-js";
import { OperationNames } from "./api";

export interface ProcessMessage<
  TData = unknown,
  TTopic extends string = string,
> {
  topic: TTopic;
  data: TData;
  origin: string | null;
}

interface Subscriber<T extends ProcessMessage> {
  filter: (msg: T) => boolean;
  callback: (msg: T) => void;
}

const subscribers: Subscriber<ProcessMessage>[] = [];

// Declare the global function on the window type
declare global {
  interface Window {
    notifyBus: (msg: ProcessMessage) => void;
  }
}

window.notifyBus = (msg: ProcessMessage) => {
  console.debug("notifyBus called with:", msg);
  for (const sub of subscribers) {
    try {
      if (sub.filter(msg)) {
        sub.callback(msg);
      }
    } catch (e) {
      console.error("Subscriber threw an error:", e);
    }
  }
};

/**
 * Subscribe to any message
 *
 * Returns a function to unsubsribe itself
 *
 * consider using useNotify for reactive usage on solidjs
 */
export function _subscribeNotify<T extends ProcessMessage>(
  filter: (msg: T) => boolean,
  callback: (msg: T) => void,
) {
  // Cast to shared subscriber type for storage
  const sub: Subscriber<ProcessMessage> = {
    filter: filter as (msg: ProcessMessage) => boolean,
    callback: callback as (msg: ProcessMessage) => void,
  };
  subscribers.push(sub);
  return () => {
    const idx = subscribers.indexOf(sub);
    if (idx >= 0) subscribers.splice(idx, 1);
  };
}

/**
 * Returns a reactive signal that tracks a message by the given filter predicate
 * The signal has the value of the last message where filter was true
 * null in case no message was recieved yet
 */
export function useNotify<T extends ProcessMessage = ProcessMessage>(
  filter: (msg: T) => boolean = () => true as boolean,
) {
  const [message, setMessage] = createSignal<T | null>(null);

  const unsubscribe = _subscribeNotify(filter, (msg) => setMessage(() => msg));

  onCleanup(unsubscribe);

  return message;
}

/**
 * Tracks any message that was sent from this api origin
 *
 */
export function useNotifyOrigin<
  T extends ProcessMessage = ProcessMessage,
  K extends OperationNames = OperationNames,
>(origin: K) {
  return useNotify<T>((m) => m.origin === origin);
}
