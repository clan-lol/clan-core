import { callApi, OperationResponse } from "@/src/api";
import { FileInput } from "@/src/components/FileInput";
import { SelectInput } from "@/src/components/SelectInput";
import { TextInput } from "@/src/components/TextInput";
import { createForm, required, FieldValues } from "@modular-forms/solid";
import { createQuery } from "@tanstack/solid-query";
import { For } from "solid-js";
import toast from "solid-toast";

interface FlashFormValues extends FieldValues {
  machine: {
    devicePath: string;
    flake: string;
  };
  disk: string;
  language: string;
  keymap: string;
  sshKeys: File[];
}

export const Flash = () => {
  const [formStore, { Form, Field }] = createForm<FlashFormValues>({
    initialValues: {
      machine: {
        flake: "git+https://git.clan.lol/clan/clan-core",
        devicePath: "flash-installer",
      },
      language: "en_US.UTF-8",
      keymap: "en",
    },
  });

  const deviceQuery = createQuery(() => ({
    queryKey: ["block_devices"],
    queryFn: async () => {
      const result = await callApi("show_block_devices", {});
      if (result.status === "error") throw new Error("Failed to fetch data");
      return result.data;
    },
    staleTime: 1000 * 60 * 1, // 1 minutes
  }));

  const keymapQuery = createQuery(() => ({
    queryKey: ["list_keymaps"],
    queryFn: async () => {
      const result = await callApi("list_possible_keymaps", {});
      if (result.status === "error") throw new Error("Failed to fetch data");
      return result.data;
    },
    staleTime: 1000 * 60 * 15, // 15 minutes
  }));

  const langQuery = createQuery(() => ({
    queryKey: ["list_languages"],
    queryFn: async () => {
      const result = await callApi("list_possible_languages", {});
      if (result.status === "error") throw new Error("Failed to fetch data");
      return result.data;
    },
    staleTime: 1000 * 60 * 15, // 15 minutes
  }));

  /**
   * Opens the custom file dialog
   * Returns a native FileList to allow interaction with the native input type="file"
   */
  const selectSshKeys = async (): Promise<FileList> => {
    const dataTransfer = new DataTransfer();

    const response = await callApi("open_file", {
      file_request: {
        title: "Select SSH Key",
        mode: "open_multiple_files",
        filters: { patterns: ["*.pub"] },
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

  const handleSubmit = async (values: FlashFormValues) => {
    console.log(
      "Submit SSH Keys:",
      values.sshKeys.map((file) => file.name),
    );
    try {
      await callApi("flash_machine", {
        machine: {
          name: values.machine.devicePath,
          flake: {
            loc: values.machine.flake,
          },
        },
        mode: "format",
        disks: { main: values.disk },
        system_config: {
          language: values.language,
          keymap: values.keymap,
          ssh_keys_path: values.sshKeys.map((file) => file.name),
        },
        dry_run: false,
        write_efi_boot_entries: false,
        debug: false,
      });
    } catch (error) {
      toast.error(`Error could not flash disk: ${error}`);
      console.error("Error submitting form:", error);
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
              <TextInput
                formStore={formStore}
                inputProps={props}
                label="Installer (flake URL)"
                value={String(field.value)}
                inlineLabel={<span class="material-icons">file_download</span>}
                error={field.error}
                required
              />
            </>
          )}
        </Field>
        <Field
          name="machine.devicePath"
          validate={[required("This field is required")]}
        >
          {(field, props) => (
            <>
              <TextInput
                formStore={formStore}
                inputProps={props}
                label="Installer Image (attribute name)"
                value={String(field.value)}
                inlineLabel={<span class="material-icons">devices</span>}
                error={field.error}
                required
              />
            </>
          )}
        </Field>
        <Field name="disk" validate={[required("This field is required")]}>
          {(field, props) => (
            <SelectInput
              formStore={formStore}
              selectProps={props}
              label="Flash Disk"
              value={String(field.value)}
              error={field.error}
              required
              options={
                <>
                  <option value="" disabled>
                    Select a disk
                  </option>
                  <For each={deviceQuery.data?.blockdevices}>
                    {(device) => (
                      <option value={device.path}>
                        {device.path} -- {device.size} bytes
                      </option>
                    )}
                  </For>
                </>
              }
            />
          )}
        </Field>
        <Field name="language" validate={[required("This field is required")]}>
          {(field, props) => (
            <>
              <SelectInput
                formStore={formStore}
                selectProps={props}
                label="Language"
                value={String(field.value)}
                error={field.error}
                required
                options={
                  <For each={langQuery.data}>
                    {(language) => <option value={language}>{language}</option>}
                  </For>
                }
              />
            </>
          )}
        </Field>
        <Field name="keymap" validate={[required("This field is required")]}>
          {(field, props) => (
            <>
              <SelectInput
                formStore={formStore}
                selectProps={props}
                label="Keymap"
                value={String(field.value)}
                error={field.error}
                required
                options={
                  <For each={keymapQuery.data}>
                    {(keymap) => <option value={keymap}>{keymap}</option>}
                  </For>
                }
              />
            </>
          )}
        </Field>

        <Field name="sshKeys" type="File[]">
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
                value={field.value}
                error={field.error}
                label="Authorized SSH Keys"
                multiple
                required
              />
            </>
          )}
        </Field>
        <button
          class="btn btn-error"
          type="submit"
          disabled={formStore.submitting}
        >
          {formStore.submitting ? (
            <span class="loading loading-spinner"></span>
          ) : (
            <span class="material-icons">bolt</span>
          )}
          {formStore.submitting ? "Flashing..." : "Flash Installer"}
        </button>
      </Form>
    </div>
  );
};
