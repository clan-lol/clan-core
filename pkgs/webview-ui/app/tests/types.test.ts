import { describe, it, expectTypeOf } from "vitest";

import { OperationNames, pyApi } from "@/src/message";

describe.concurrent("API types work properly", () => {
  // Test some basic types
  it("distinct success/error unions", async () => {
    const k: OperationNames = "create_clan" as OperationNames; // Just a random key, since
    expectTypeOf(pyApi[k].receive).toBeFunction();
    expectTypeOf(pyApi[k].receive).parameter(0).toBeFunction();
    // receive is a function that takes a function, which takes the response parameter
    expectTypeOf(pyApi[k].receive)
      .parameter(0)
      .parameter(0)
      .toMatchTypeOf<
        { status: "success"; data?: any } | { status: "error"; errors: any[] }
      >();
  });

  it("Cannot access data of error response", async () => {
    const k: OperationNames = "create_clan" as OperationNames; // Just a random key, since
    expectTypeOf(pyApi[k].receive).toBeFunction();
    expectTypeOf(pyApi[k].receive).parameter(0).toBeFunction();
    expectTypeOf(pyApi[k].receive).parameter(0).parameter(0).toMatchTypeOf<
      // @ts-expect-error: data is not defined in error responses
      | { status: "success"; data?: any }
      | { status: "error"; errors: any[]; data: any }
    >();
  });

  it("Machine list receives a list of names/id string", async () => {
    expectTypeOf(pyApi.list_machines.receive)
      .parameter(0)
      .parameter(0)
      .toMatchTypeOf<
        { status: "success"; data: string[] } | { status: "error"; errors: any }
      >();
  });

  it("Machine show receives an object with at least: machine_name, machine_description and machine_icon", async () => {
    expectTypeOf(pyApi.show_machine.receive)
      .parameter(0)
      .parameter(0)
      .toMatchTypeOf<
        | {
            status: "success";
            data: {
              machine_name: string;
              machine_icon?: string | null;
              machine_description?: string | null;
            };
          }
        | { status: "error"; errors: any }
      >();
  });
});
