import { route } from "@/src/App";
import { OperationArgs, OperationResponse, pyApi } from "@/src/api";
import { SubmitHandler, createForm, required } from "@modular-forms/solid";
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

  const [devices, setDevices] = createSignal<BlockDevices>([]);
  // pyApi.show_block_devices.receive((r) => {
  //   console.log("block devices", r);
  //   if (r.status === "success") {
  //     setDevices(r.data.blockdevices);
  //   }
  // });

  const handleSubmit: SubmitHandler<FlashFormValues> = (values, event) => {
    // pyApi.open_file.dispatch({ file_request: { mode: "save" } });
    // pyApi.open_file.receive((r) => {
    //   if (r.status === "success") {
    //     if (r.data) {
    //       pyApi.create_clan.dispatch({
    //         options: { directory: r.data, meta: values },
    //       });
    //     }
    //     return;
    //   }
    // });
    console.log("submit", values);
  };

  // effect(() => {
  //   if (route() === "flash") {
  //     pyApi.show_block_devices.dispatch({});
  //   }
  // });
  return (
    <div class="">
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
                  placeholder="Clan URI"
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
                  placeholder="Machine Name"
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
                <select required class="select w-full" {...props}>
                  {/* <span class="material-icons">devices</span> */}
                  <For each={devices()}>
                    {(device) => (
                      <option value={device.name}>
                        {device.name} / {device.size} bytes
                      </option>
                    )}
                  </For>
                </select>
                <div class="label">
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
