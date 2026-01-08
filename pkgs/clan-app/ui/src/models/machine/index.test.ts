import { describe, test, vi } from "vitest";
import { testEffect } from "@solidjs/testing-library";
import { createEffect } from "solid-js";
import { createMachinesStoreFixture } from "@/src/tests/utils";

describe("machines", () => {
  test("activate", ({ expect }) => {
    return testEffect((done) => {
      const [
        [machines, machinesMethods],
        [clan, clanMethods],
        [clans, clansMethods],
      ] = createMachinesStoreFixture({
        foo: {
          data: {
            deploy: {
              buildHost: null,
              targetHost: null,
            },
            description: "",
            machineClass: "nixos",
            tags: [],
            position: [0, 0],
          },
          dataSchema: {},
          status: "not_installed",
        },
      });
      const fooMachine = () => machines().all.foo;

      createEffect((runNum: number) => {
        [
          () => {
            expect(fooMachine().isActive).toBe(false);
            machinesMethods.activateMachine("foo");
          },
          () => {
            expect(fooMachine().isActive).toBe(true);
            done();
          },
        ][runNum]?.();
        return runNum + 1;
      }, 0);
    });
  });
  test("highlight", ({ expect }) => {
    return testEffect((done) => {
      const [
        [machines, machinesMethods],
        [clan, clanMethods],
        [clans, clansMethods],
      ] = createMachinesStoreFixture({
        foo: {
          data: {
            deploy: {
              buildHost: null,
              targetHost: null,
            },
            description: "",
            machineClass: "nixos",
            tags: [],
            position: [0, 0],
          },
          dataSchema: {},
          status: "not_installed",
        },
      });

      const fooMachine = () => machines().all.foo;

      createEffect((runNum: number) => {
        [
          () => {
            expect(fooMachine().isHighlighted).toBe(false);
            machinesMethods.setHighlightedMachines("foo");
          },
          () => {
            expect(fooMachine().isHighlighted).toBe(true);
            done();
          },
        ][runNum]?.();
        return runNum + 1;
      }, 0);
    });
  });
});
