import { callApi, SuccessData } from "@/src/api";
import { activeURI } from "@/src/App";
import { FileInput } from "@/src/components/FileInput";
import { SelectInput } from "@/src/components/SelectInput";
import { TextInput } from "@/src/components/TextInput";
import { createForm, getValue, reset } from "@modular-forms/solid";
import { useParams } from "@solidjs/router";
import { createQuery } from "@tanstack/solid-query";
import { createSignal, For, Show, createEffect } from "solid-js";
import toast from "solid-toast";

// eslint-disable-next-line @typescript-eslint/consistent-type-definitions
type MachineFormInterface = {
  name: string;
  description: string;
  targetHost?: string;
  sshKey?: File;
  disk?: string;
};

type Disks = SuccessData<"show_block_devices">["data"]["blockdevices"];

/**
 * Opens the custom file dialog
 * Returns a native FileList to allow interaction with the native input type="file"
 */
const selectSshKeys = async (): Promise<FileList> => {
  const dataTransfer = new DataTransfer();

  const response = await callApi("open_file", {
    file_request: {
      title: "Select SSH Key",
      mode: "open_file",
      initial_folder: "~/.ssh",
    },
  });
  if (response.status === "success" && response.data) {
    // Add synthetic files to the DataTransfer object
    // FileList cannot be instantiated directly.
    response.data.forEach((filename) => {
      dataTransfer.items.add(new File([], filename));
    });
  }
  return dataTransfer.files;
};

// eslint-disable-next-line @typescript-eslint/consistent-type-definitions
type InstallForm = { disk?: string };

interface InstallMachineProps {
  name?: string;
  targetHost?: string;
  sshKey?: File;
  disks: Disks;
}
const InstallMachine = (props: InstallMachineProps) => {
  const diskPlaceholder = "Select the boot disk of the remote machine";

  const [formStore, { Form, Field }] = createForm<InstallForm>();

  const hasDisk = () => getValue(formStore, "disk") !== diskPlaceholder;

  const [confirmDisk, setConfirmDisk] = createSignal(!hasDisk());

  const handleInstall = async (values: InstallForm) => {
    console.log("Installing", values);
  };
  return (
    <>
      <Form onSubmit={handleInstall}>
        <h3 class="text-lg font-bold">{props.name}</h3>
        <p class="py-4">Install to {props.targetHost}</p>
        <p class="py-4">
          Using {props.sshKey?.name || "default ssh key"} for authentication
        </p>
        <Field name="disk">
          {(field, fieldProps) => (
            <SelectInput
              formStore={formStore}
              selectProps={{
                ...fieldProps,
                // @ts-expect-error: disabled is supported by htmlSelect
                disabled: confirmDisk(),
              }}
              label="Remote Disk to use"
              value={String(field.value)}
              error={field.error}
              required
              options={
                <>
                  <option disabled>{diskPlaceholder}</option>
                  <For each={props.disks}>
                    {(dev) => (
                      <option value={dev.name}>
                        {dev.name}
                        {" -- "}
                        {dev.size}
                        {"bytes @"}
                        {props.targetHost?.split("@")?.[1]}
                      </option>
                    )}
                  </For>
                </>
              }
            />
          )}
        </Field>
        <div class="modal-action">
          <Show
            when={confirmDisk()}
            fallback={
              <button
                class="btn btn-primary btn-wide"
                onClick={() => setConfirmDisk(true)}
                disabled={!hasDisk()}
              >
                <span class="material-icons">check</span>
                Confirm Disk
              </button>
            }
          >
            <button class="btn btn-primary btn-wide" type="submit">
              <span class="material-icons">send_to_mobile</span>
              Install
            </button>
          </Show>
          <form method="dialog">
            <button onClick={() => setConfirmDisk(false)} class="btn">
              Close
            </button>
          </form>
        </div>
      </Form>
    </>
  );
};

interface MachineDetailsProps {
  initialData: MachineFormInterface;
}
const MachineForm = (props: MachineDetailsProps) => {
  const [formStore, { Form, Field }] = createForm<MachineFormInterface>({
    initialValues: props.initialData,
  });

  const sshKey = () => getValue(formStore, "sshKey");
  const targetHost = () => getValue(formStore, "targetHost");
  const machineName = () =>
    getValue(formStore, "name") || props.initialData.name;

  const onlineStatusQuery = createQuery(() => ({
    queryKey: [activeURI(), "machine", targetHost(), "check_machine_online"],
    queryFn: async () => {
      const curr = activeURI();
      if (curr) {
        const result = await callApi("check_machine_online", {
          flake_url: curr,
          machine_name: machineName(),
          opts: {
            keyfile: sshKey()?.name,
          },
        });
        if (result.status === "error") throw new Error("Failed to fetch data");
        return result.data;
      }
    },
    refetchInterval: 5000,
  }));

  const online = () => onlineStatusQuery.data === "Online";

  const remoteDiskQuery = createQuery(() => ({
    queryKey: [
      activeURI(),
      "machine",
      machineName(),
      targetHost(),
      "show_block_devices",
    ],
    enabled: online(),
    queryFn: async () => {
      const curr = activeURI();
      if (curr) {
        const result = await callApi("show_block_devices", {
          options: {
            hostname: targetHost(),
            keyfile: sshKey()?.name,
          },
        });
        if (result.status === "error") throw new Error("Failed to fetch data");
        return result.data;
      }
    },
  }));

  const handleSubmit = async (values: MachineFormInterface) => {
    const curr_uri = activeURI();
    if (!curr_uri) {
      return;
    }

    const machine_response = await callApi("set_machine", {
      flake_url: curr_uri,
      machine_name: props.initialData.name,
      machine: {
        name: values.name,
        description: values.description,
        deploy: {
          targetHost: values.targetHost,
        },
      },
    });
    if (machine_response.status === "error") {
      toast.error(
        `Failed to set machine: ${machine_response.errors[0].message}`
      );
    }
    if (machine_response.status === "success") {
      toast.success("Machine set successfully");
    }

    return null;
  };
  return (
    <div class="m-2 w-full max-w-xl">
      <Form onSubmit={handleSubmit}>
        <div class="flex w-full justify-center p-2">
          <div
            class="avatar placeholder"
            classList={{
              online: onlineStatusQuery.data === "Online",
              offline: onlineStatusQuery.data === "Offline",
            }}
          >
            <div class="w-24 rounded-full bg-neutral text-neutral-content">
              <Show
                when={onlineStatusQuery.isFetching}
                fallback={<span class="material-icons text-4xl">devices</span>}
              >
                <span class="loading loading-bars loading-sm justify-self-end"></span>
              </Show>
            </div>
          </div>
        </div>
        <div class="my-2 w-full text-2xl">Details</div>
        <Field name="name">
          {(field, props) => (
            <TextInput
              formStore={formStore}
              inputProps={props}
              label="Name"
              value={field.value ?? ""}
              error={field.error}
              class="col-span-2"
              required
            />
          )}
        </Field>
        <Field name="description">
          {(field, props) => (
            <TextInput
              formStore={formStore}
              inputProps={props}
              label="Description"
              value={field.value ?? ""}
              error={field.error}
              class="col-span-2"
              required
            />
          )}
        </Field>

        <div class="collapse collapse-arrow" tabindex="0">
          <input type="checkbox" />
          <div class="collapse-title link px-0 text-xl ">
            Connection Settings
          </div>
          <div class="collapse-content">
            <Field name="targetHost">
              {(field, props) => (
                <TextInput
                  formStore={formStore}
                  inputProps={props}
                  label="Target Host"
                  value={field.value ?? ""}
                  error={field.error}
                  class="col-span-2"
                  required
                />
              )}
            </Field>
            <Field name="sshKey" type="File">
              {(field, props) => (
                <>
                  <FileInput
                    {...props}
                    onClick={async (event) => {
                      event.preventDefault(); // Prevent the native file dialog from opening
                      const input = event.target;
                      const files = await selectSshKeys();

                      // Set the files
                      Object.defineProperty(input, "files", {
                        value: files,
                        writable: true,
                      });
                      // Define the files property on the input element
                      const changeEvent = new Event("input", {
                        bubbles: true,
                        cancelable: true,
                      });
                      input.dispatchEvent(changeEvent);
                    }}
                    placeholder={"When empty the default key(s) will be used"}
                    value={field.value}
                    error={field.error}
                    helperText="Provide the SSH key used to connect to the machine"
                    label="SSH Key"
                  />
                </>
              )}
            </Field>
          </div>
        </div>

        <div class="my-2 w-full">
          <button
            class="btn btn-primary btn-wide"
            type="submit"
            disabled={!formStore.dirty}
          >
            Save
          </button>
        </div>
      </Form>
      <div class="my-2 w-full text-2xl">Remote Interactions</div>
      <div class="my-2 flex w-full flex-col gap-2">
        <span class="max-w-md text-neutral">
          Installs the system for the first time. Used to bootstrap the remote
          device.
        </span>
        <div class="tooltip w-fit" data-tip="Machine must be online">
          <button
            class="btn btn-primary btn-sm btn-wide"
            disabled={!online()}
            // @ts-expect-error: This string method is not supported by ts
            onClick="install_modal.showModal()"
          >
            <span class="material-icons">send_to_mobile</span>
            Install
          </button>
        </div>

        <dialog id="install_modal" class="modal">
          <div class="modal-box w-11/12 max-w-5xl">
            <InstallMachine
              name={machineName()}
              sshKey={sshKey()}
              targetHost={getValue(formStore, "targetHost")}
              disks={remoteDiskQuery.data?.blockdevices || []}
            />
          </div>
        </dialog>

        <span class="max-w-md text-neutral">
          Installs the system for the first time. Used to bootstrap the remote
          device.
        </span>
        <div class="tooltip w-fit" data-tip="Machine must be online">
          <button class="btn btn-primary btn-sm btn-wide" disabled={!online()}>
            <span class="material-icons">update</span>
            Update
          </button>
        </div>
      </div>
    </div>
  );
};

export const MachineDetails = () => {
  const params = useParams();
  const query = createQuery(() => ({
    queryKey: [
      activeURI(),
      "machine",
      params.id,
      "get_inventory_machine_details",
    ],
    queryFn: async () => {
      const curr = activeURI();
      if (curr) {
        const result = await callApi("get_inventory_machine_details", {
          flake_url: curr,
          machine_name: params.id,
        });
        if (result.status === "error") throw new Error("Failed to fetch data");
        return result.data;
      }
    },
  }));

  return (
    <>
      <Show
        when={query.data}
        fallback={<span class="loading loading-lg"></span>}
      >
        <MachineForm
          initialData={{
            name: query.data?.machine.name ?? "",
            description: query.data?.machine.description ?? "",
            targetHost: query.data?.machine.deploy.targetHost ?? "",
          }}
        />
      </Show>
    </>
  );
};
