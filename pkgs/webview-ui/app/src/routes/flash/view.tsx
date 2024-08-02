import { route } from "@/src/App";
import { callApi, OperationArgs, OperationResponse, pyApi } from "@/src/api";
import {
  createForm,
  required,
  setValue,
  SubmitHandler,
} from "@modular-forms/solid";
import { createQuery } from "@tanstack/solid-query";
import { createEffect, createSignal, For } from "solid-js";
import { effect } from "solid-js/web";

type FlashFormValues = {
  machine: {
    devicePath: string;
    flake: string;
  };
  disk: string;
  language: string;
  keymap: string;
  sshKeys: string[];
};

type BlockDevices = Extract<
  OperationResponse<"show_block_devices">,
  { status: "success" }
>["data"]["blockdevices"];

export const Flash = () => {
  const [formStore, { Form, Field }] = createForm<FlashFormValues>({});
  const [sshKeys, setSshKeys] = createSignal<string[]>([]);
  const [isFlashing, setIsFlashing] = createSignal(false);

  const selectSshPubkey = async () => {
    try {
      const loc = await callApi("open_file", {
        file_request: {
          title: "Select SSH Key",
          mode: "open_multiple_files",
          filters: { patterns: ["*.pub"] },
          initial_folder: "~/.ssh",
        },
      });
      console.log({ loc }, loc.status);
      if (loc.status === "success" && loc.data) {
        setSshKeys(loc.data);
        return loc.data;
      }
    } catch (e) {
      //
    }
  };

  // Create an effect that updates the form when externalUsername changes
  createEffect(() => {
    const newSshKeys = sshKeys();
    if (newSshKeys) {
      setValue(formStore, "sshKeys", newSshKeys);
    }
  });

  const {
    data: devices,
    isFetching,
  } = createQuery(() => ({
    queryKey: ["block_devices"],
    queryFn: async () => {
      const result = await callApi("show_block_devices", {});
      if (result.status === "error") throw new Error("Failed to fetch data");
      return result.data;
    },
    staleTime: 1000 * 60 * 2, // 1 minutes
  }));

  const {
    data: keymaps,
    isFetching: isFetchingKeymaps,
  } = createQuery(() => ({
    queryKey: ["list_keymaps"],
    queryFn: async () => {
      const result = await callApi("list_possible_keymaps", {});
      if (result.status === "error") throw new Error("Failed to fetch data");
      return result.data;
    },
    staleTime: 1000 * 60 * 15, // 15 minutes
  }));

  const {
    data: languages,
    isFetching: isFetchingLanguages,
  } = createQuery(() => ({
    queryKey: ["list_languages"],
    queryFn: async () => {
      const result = await callApi("list_possible_languages", {});
      if (result.status === "error") throw new Error("Failed to fetch data");
      return result.data;
    },
    staleTime: 1000 * 60 * 15, // 15 minutes
  }));

  const handleSubmit = async (values: FlashFormValues) => {
    setIsFlashing(true);
    try {
      await callApi("flash_machine", {
        machine: {
          name: values.machine.devicePath,
          flake: {
            loc: values.machine.flake,
          },
        },
        mode: "format",
        disks: { "main": values.disk },
        system_config: {
          language: values.language,
          keymap: values.keymap,
          ssh_keys_path: values.sshKeys,
        },
        dry_run: false,
        write_efi_boot_entries: false,
        debug: false,
      });
    } catch (error) {
      console.error("Error submitting form:", error);
    } finally {
      setIsFlashing(false);
    }
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
                  //placeholder="machine.flake"
                  value="git+https://git.clan.lol/clan/clan-core"
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
          name="machine.devicePath"
          validate={[required("This field is required")]}
        >
          {(field, props) => (
            <>
              <label class="input input-bordered flex items-center gap-2">
                <span class="material-icons">devices</span>
                <input
                  type="text"
                  class="grow"
                  value="flash-installer"
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
                  <option value="" disabled>Select a disk</option>
                  <For each={devices?.blockdevices}>
                    {(device) => (
                      <option value={device.path}>
                        {device.path} -- {device.size} bytes
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
        <Field name="language" validate={[required("This field is required")]}>
          {(field, props) => (
            <>
              <label class="form-control input-bordered flex w-full items-center gap-2">
                <select
                  required
                  class="select select-bordered w-full"
                  {...props}
                >
                  <option>en_US.UTF-8</option>
                  <For each={languages}>
                    {(language) => (
                      <option value={language}>
                        {language}
                      </option>
                    )}
                  </For>
                </select>
                <div class="label">
                  {isFetchingLanguages && (
                    <span class="label-text-alt">
                      <span class="loading loading-bars">en_US.UTF-8</span>
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
        <Field name="keymap" validate={[required("This field is required")]}>
          {(field, props) => (
            <>
              <label class="form-control input-bordered flex w-full items-center gap-2">
                <select
                  required
                  class="select select-bordered w-full"
                  {...props}
                >
                  <option>en</option>
                  <For each={keymaps}>
                    {(keymap) => (
                      <option value={keymap}>
                        {keymap}
                      </option>
                    )}
                  </For>
                </select>
                <div class="label">
                  {isFetchingKeymaps && (
                    <span class="label-text
                    -alt">
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
        <Field name="sshKeys" validate={[]} type="string[]">
          {(field, props) => (
            <>
              <label class="input input-bordered flex items-center gap-2">
                <span class="material-icons">key</span>
                <input
                  type="text"
                  class="grow"
                  placeholder="Select SSH Key"
                  value={field.value ? field.value.join(", ") : ""}
                  readOnly
                  onClick={() => selectSshPubkey()}
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
        <button class="btn btn-error" type="submit" disabled={isFlashing()}>
          {isFlashing()
            ? <span class="loading loading-spinner"></span>
            : <span class="material-icons">bolt</span>}
          {isFlashing() ? "Flashing..." : "Flash Installer"}
        </button>
      </Form>
    </div>
  );
};
