import { route } from "@/src/App";
import { OperationArgs, OperationResponse, callApi, pyApi } from "@/src/api";
import { SubmitHandler, createForm, required } from "@modular-forms/solid";
import { createQuery } from "@tanstack/solid-query";
import { For, createSignal } from "solid-js";
import { effect } from "solid-js/web";

// type FlashMachineArgs = {
//   machine: Omit<OperationArgs<"flash_machine">["machine"], "cached_deployment">;
// } & Omit<Omit<OperationArgs<"flash_machine">, "machine">, "system_config">;

// type FlashMachineArgs = OperationArgs<"flash_machine">;

// type k = keyof FlashMachineArgs;
// eslint-disable-next-line @typescript-eslint/consistent-type-definitions
type FlashFormValues = {
  machine: {
    name: string;
    flake: string;
  };
  disk: string;
};

type BlockDevices = Extract<
  OperationResponse<"show_block_devices">,
  { status: "success" }
>["data"]["blockdevices"];

export const Flash = () => {
  const [formStore, { Form, Field }] = createForm<FlashFormValues>({});

  const {
    data: devices,
    refetch: loadDevices,
    isFetching,
  } = createQuery(() => ({
    queryKey: ["TanStack Query"],
    queryFn: async () => {
      const result = await callApi("show_block_devices", {});
      if (result.status === "error") throw new Error("Failed to fetch data");
      return result.data;
    },
    staleTime: 1000 * 60 * 1, // 1 minutes
  }));

  const handleSubmit = async (values: FlashFormValues) => {
    // TODO: Rework Flash machine API
    // Its unusable in its current state
    // await callApi("flash_machine", {
    //   machine: {
    //     name: "",
    //   },
    //   disks:  {values.disk },
    //   dry_run: true,
    // });
    console.log("submit", values);
  };

  return (
    <div class="px-2">
      <Form onSubmit={handleSubmit}>
        <Field
          name="machine.flake"
          validate={[required("This field is required")]}
        >
          {(field, props) => (
            <>
              <label class="input input-bordered flex items-center gap-2">
                <span class="material-icons">file_download</span>
                <input
                  type="text"
                  class="grow"
                  placeholder="machine.flake"
                  required
                  {...props}
                />
              </label>
              <div class="label">
                {field.error && (
                  <span class="label-text-alt font-bold text-error">
                    {field.error}
                  </span>
                )}
              </div>
            </>
          )}
        </Field>
        <Field
          name="machine.name"
          validate={[required("This field is required")]}
        >
          {(field, props) => (
            <>
              <label class="input input-bordered flex items-center gap-2">
                <span class="material-icons">devices</span>
                <input
                  type="text"
                  class="grow"
                  placeholder="machine.name"
                  required
                  {...props}
                />
              </label>
              <div class="label">
                {field.error && (
                  <span class="label-text-alt font-bold text-error">
                    {field.error}
                  </span>
                )}
              </div>
            </>
          )}
        </Field>
        <Field name="disk" validate={[required("This field is required")]}>
          {(field, props) => (
            <>
              <label class="form-control input-bordered flex w-full items-center gap-2">
                <select
                  required
                  class="select select-bordered w-full"
                  {...props}
                >
                  {/* <span class="material-icons">devices</span> */}
                  <option disabled>Select a disk</option>

                  <For each={devices?.blockdevices}>
                    {(device) => (
                      <option value={device.name}>
                        {device.name} / {device.size} bytes
                      </option>
                    )}
                  </For>
                </select>
                <div class="label">
                  {isFetching && (
                    <span class="label-text-alt">
                      <span class="loading loading-bars"></span>
                    </span>
                  )}
                  {field.error && (
                    <span class="label-text-alt font-bold text-error">
                      {field.error}
                    </span>
                  )}
                </div>
              </label>
            </>
          )}
        </Field>
        <button class="btn btn-error" type="submit">
          <span class="material-icons">bolt</span>Flash Installer
        </button>
      </Form>
    </div>
  );
};
