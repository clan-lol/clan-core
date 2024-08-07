import { callApi, OperationResponse } from "@/src/api";
import { FileInput } from "@/src/components/FileInput";
import { SelectInput } from "@/src/components/SelectInput";
import { TextInput } from "@/src/components/TextInput";
import {
  createForm,
  required,
  FieldValues,
  setValue,
  getValue,
} from "@modular-forms/solid";
import { createQuery } from "@tanstack/solid-query";
import { createEffect, createSignal, For } from "solid-js";
import toast from "solid-toast";

interface Wifi extends FieldValues {
  ssid: string;
  password: string;
}

interface FlashFormValues extends FieldValues {
  machine: {
    devicePath: string;
    flake: string;
  };
  disk: string;
  language: string;
  keymap: string;
  wifi: Wifi[];
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

  /* ==== WIFI NETWORK ==== */
  const [wifiNetworks, setWifiNetworks] = createSignal<Wifi[]>([]);
  const [passwordVisibility, setPasswordVisibility] = createSignal<boolean[]>(
    [],
  );

  createEffect(() => {
    const formWifi = getValue(formStore, "wifi");
    if (formWifi !== undefined) {
      setWifiNetworks(formWifi as Wifi[]);
      setPasswordVisibility(new Array(formWifi.length).fill(false));
    }
  });

  const addWifiNetwork = () => {
    const updatedNetworks = [...wifiNetworks(), { ssid: "", password: "" }];
    setWifiNetworks(updatedNetworks);
    setPasswordVisibility([...passwordVisibility(), false]);
    setValue(formStore, "wifi", updatedNetworks);
  };

  const removeWifiNetwork = (index: number) => {
    const updatedNetworks = wifiNetworks().filter((_, i) => i !== index);
    setWifiNetworks(updatedNetworks);
    const updatedVisibility = passwordVisibility().filter(
      (_, i) => i !== index,
    );
    setPasswordVisibility(updatedVisibility);
    setValue(formStore, "wifi", updatedNetworks);
  };

  const togglePasswordVisibility = (index: number) => {
    const updatedVisibility = [...passwordVisibility()];
    updatedVisibility[index] = !updatedVisibility[index];
    setPasswordVisibility(updatedVisibility);
  };
  /* ==== END OF WIFI NETWORK ==== */

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
    console.log("Submit WiFi Networks:", values.wifi);
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
          wifi_settings: values.wifi.map((network) => ({
            ssid: network.ssid,
            password: network.password,
          })),
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

        {/* WiFi Networks */}
        <div class="mb-4">
          <h3 class="text-lg font-semibold mb-2">WiFi Networks</h3>
          <For each={wifiNetworks()}>
            {(network, index) => (
              <div class="flex gap-2 mb-2">
                <Field
                  name={`wifi.${index()}.ssid`}
                  validate={[required("SSID is required")]}
                >
                  {(field, props) => (
                    <TextInput
                      formStore={formStore}
                      inputProps={props}
                      label="SSID"
                      value={field.value ?? ""}
                      error={field.error}
                      required
                    />
                  )}
                </Field>
                <Field
                  name={`wifi.${index()}.password`}
                  validate={[required("Password is required")]}
                >
                  {(field, props) => (
                    <div class="relative w-full">
                      <TextInput
                        formStore={formStore}
                        inputProps={props}
                        type={
                          passwordVisibility()[index()] ? "text" : "password"
                        }
                        label="Password"
                        value={field.value ?? ""}
                        error={field.error}
                        required
                      />
                      <button
                        type="button"
                        class="absolute inset-y-14 right-0 pr-3 flex items-center text-sm leading-5"
                        onClick={() => togglePasswordVisibility(index())}
                      >
                        <span class="material-icons">
                          {passwordVisibility()[index()]
                            ? "visibility_off"
                            : "visibility"}
                        </span>
                      </button>
                    </div>
                  )}
                </Field>
                <button
                  type="button"
                  class="btn btn-error"
                  onClick={() => removeWifiNetwork(index())}
                >
                  <span class="material-icons">delete</span>
                </button>
              </div>
            )}
          </For>
          <button
            type="button"
            class="btn btn-primary"
            onClick={addWifiNetwork}
          >
            <span class="material-icons">add</span> Add WiFi Network
          </button>
        </div>

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
