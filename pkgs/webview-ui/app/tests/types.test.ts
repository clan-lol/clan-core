import { describe, expectTypeOf, it } from "vitest";

import { OperationNames, pyApi } from "@/src/api";

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

  it("Machine list receives a records of names and machine info.", async () => {
    expectTypeOf(pyApi.list_inventory_machines.receive)
      .parameter(0)
      .parameter(0)
      .toMatchTypeOf<
        | { status: "success"; data: Record<string, object> }
        | { status: "error"; errors: any }
      >();
  });
});
