import { query } from "@solidjs/router";
import set = query.set;
import FakeTimers, { Clock } from "@sinonjs/fake-timers";

export interface StorybookClock {
  tick: (ms: number) => void;
  setTimeout: (
    callback: (...args: any[]) => void,
    delay: number,
    ...args: any[]
  ) => void;
}

class BrowserClock implements StorybookClock {
  setTimeout(
    callback: (...args: any[]) => void,
    delay: number,
    args: any,
  ): void {
    // set a normal timeout
    setTimeout(callback, delay, args);
  }

  tick(_: number): void {
    // do nothing
  }
}

class FakeClock implements StorybookClock {
  private clock: Clock;

  constructor() {
    this.clock = FakeTimers.createClock();
  }

  setTimeout(
    callback: (...args: any[]) => void,
    delay: number,
    args: any,
  ): void {
    this.clock.setTimeout(callback, delay, args);
  }

  tick(ms: number): void {
    this.clock.tick(ms);
  }
}

export function StorybookClock(): StorybookClock {
  // Check if we're in a browser environment
  const isBrowser = process.env.NODE_ENV !== "test";

  console.log("is browser", isBrowser);

  return isBrowser ? new BrowserClock() : new FakeClock();
}
