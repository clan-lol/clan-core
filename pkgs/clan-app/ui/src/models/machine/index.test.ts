import { describe, test, vi } from "vitest";
import { testEffect } from "@solidjs/testing-library";
import { createEffect } from "solid-js";
import { createMachinesStoreFixture } from "@/src/tests/utils";
import { createMachineStore } from "./machine";

describe("machines", () => {
  test("activate", ({ expect }) => {
    return testEffect((done) => {
      const [
        [machines, machinesMethods],
        [clan, clanMethods],
        [clans, clansMethods],
      ] = createMachinesStoreFixture({
        foo: {
          id: "foo",
          data: {
            deploy: {},
            machineClass: "nixos",
            tags: [],
            position: [0, 0],
          },
          dataSchema: {},
          status: "not_installed",
        },
      });

      const [fooMachine, fooMachineMethods] = createMachineStore(
        () => machines().all.foo!,
        [machines, machinesMethods],
        [clan, clanMethods],
        [clans, clansMethods],
      );

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
          id: "foo",
          data: {
            deploy: {},
            machineClass: "nixos",
            tags: [],
            position: [0, 0],
          },
          dataSchema: {},
          status: "not_installed",
        },
      });

      const [fooMachine, fooMachineMethods] = createMachineStore(
        () => machines().all.foo!,
        [machines, machinesMethods],
        [clan, clanMethods],
        [clans, clansMethods],
      );

      createEffect((runNum: number) => {
        [
          () => {
            expect(fooMachine().isHighlighted).toBe(false);
            machinesMethods.highlightMachines("foo");
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
