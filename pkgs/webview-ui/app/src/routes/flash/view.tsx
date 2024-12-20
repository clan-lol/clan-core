import { callApi } from "@/src/api";
import { Button } from "@/src/components/button";
import { FileInput } from "@/src/components/FileInput";
import Icon from "@/src/components/icon";

import { Typography } from "@/src/components/Typography";
import { Header } from "@/src/layout/header";

import { SelectInput } from "@/src/Form/fields/Select";
import { TextInput } from "@/src/Form/fields/TextInput";
import {
  createForm,
  required,
  FieldValues,
  setValue,
  getValue,
} from "@modular-forms/solid";
import { createQuery } from "@tanstack/solid-query";
import { createEffect, createSignal, For, Show } from "solid-js";
import toast from "solid-toast";
import { FieldLayout } from "@/src/Form/fields/layout";
import { InputLabel } from "@/src/components/inputBase";

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
    setWifiNetworks((c) => {
      const res = [...c, { ssid: "", password: "" }];
      setValue(formStore, "wifi", res);
      return res;
    });
    setPasswordVisibility((c) => [...c, false]);
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
    staleTime: Infinity,
  }));

  const langQuery = createQuery(() => ({
    queryKey: ["list_languages"],
    queryFn: async () => {
      const result = await callApi("list_possible_languages", {});
      if (result.status === "error") throw new Error("Failed to fetch data");
      return result.data;
    },
    staleTime: Infinity,
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
    console.log("Submit:", values);
    toast.error("Not fully implemented yet");
    // Disabled for now. To prevent accidental flashing of local disks
    // try {
    //   await callApi("flash_machine", {
    //     machine: {
    //       name: values.machine.devicePath,
    //       flake: {
    //         loc: values.machine.flake,
    //       },
    //     },
    //     mode: "format",
    //     disks: [{ name: "main", device: values.disk }],
    //     system_config: {
    //       language: values.language,
    //       keymap: values.keymap,
    //       ssh_keys_path: values.sshKeys.map((file) => file.name),
    //     },
    //     dry_run: false,
    //     write_efi_boot_entries: false,
    //     debug: false,
    //   });
    // } catch (error) {
    //   toast.error(`Error could not flash disk: ${error}`);
    //   console.error("Error submitting form:", error);
    // }
  };

  return (
    <>
      <Header title="Flash installer" />
      <div class="p-4">
        <Typography tag="p" hierarchy="body" size="default" color="primary">
          USB Utility image.
        </Typography>
        <Typography tag="p" hierarchy="body" size="default" color="secondary">
          Will make bootstrapping new machines easier by providing secure remote
          connection to any machine when plugged in.
        </Typography>
        <Form onSubmit={handleSubmit}>
          <div class="my-4">
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
                    helperText="Provide your SSH public key. For secure and passwordless SSH connections."
                    label="Authorized SSH Keys"
                    multiple
                    required
                  />
                </>
              )}
            </Field>
          </div>

          <Field name="disk" validate={[required("This field is required")]}>
            {(field, props) => (
              <SelectInput
                loading={deviceQuery.isFetching}
                selectProps={props}
                label="Flash Disk"
                labelProps={{
                  labelAction: (
                    <Button
                      class="ml-auto"
                      variant="ghost"
                      size="s"
                      type="button"
                      startIcon={<Icon icon="Update" />}
                      onClick={() => deviceQuery.refetch()}
                    />
                  ),
                }}
                value={field.value || ""}
                error={field.error}
                required
                placeholder="Select a thing where the installer will be flashed to"
                options={
                  deviceQuery.data?.blockdevices.map((d) => ({
                    value: d.path,
                    label: `${d.path} -- ${d.size} bytes`,
                  })) || []
                }
              />
            )}
          </Field>

          {/* WiFi Networks */}
          <div class="my-4 py-2">
            <FieldLayout
              label={<InputLabel class="mb-4">Networks</InputLabel>}
              field={
                <>
                  <Button
                    type="button"
                    size="s"
                    variant="light"
                    onClick={addWifiNetwork}
                    startIcon={<Icon icon="Plus" />}
                  >
                    WiFi Network
                  </Button>
                </>
              }
            />
            <For each={wifiNetworks()}>
              {(network, index) => (
                <div class="flex w-full gap-2">
                  <div class="mb-2 grid w-full grid-cols-6 gap-2 align-middle">
                    <Field
                      name={`wifi.${index()}.ssid`}
                      validate={[required("SSID is required")]}
                    >
                      {(field, props) => (
                        <TextInput
                          inputProps={props}
                          label="SSID"
                          value={field.value ?? ""}
                          error={field.error}
                          class="col-span-3"
                          required
                        />
                      )}
                    </Field>
                    <Field
                      name={`wifi.${index()}.password`}
                      validate={[required("Password is required")]}
                    >
                      {(field, props) => (
                        <div class="relative col-span-3 w-full">
                          <TextInput
                            inputProps={{
                              ...props,
                              type: passwordVisibility()[index()]
                                ? "text"
                                : "password",
                            }}
                            label="Password"
                            value={field.value ?? ""}
                            error={field.error}
                            // adornment={{
                            //   position: "end",
                            //   content: (
                            //     <Button
                            //       variant="light"
                            //       type="button"
                            //       class="flex justify-center opacity-70"
                            //       onClick={() =>
                            //         togglePasswordVisibility(index())
                            //       }
                            //       startIcon={
                            //         passwordVisibility()[index()] ? (
                            //           <Icon icon="EyeClose" />
                            //         ) : (
                            //           <Icon icon="EyeOpen" />
                            //         )
                            //       }
                            //     ></Button>
                            //   ),
                            // }}
                            required
                          />
                        </div>
                      )}
                    </Field>
                  </div>
                  <Button
                    type="button"
                    variant="light"
                    class="h-10"
                    size="s"
                    onClick={() => removeWifiNetwork(index())}
                    startIcon={<Icon icon="Trash" />}
                  ></Button>
                </div>
              )}
            </For>
          </div>

          <div class="collapse collapse-arrow" tabindex="0">
            <input type="checkbox" />
            <div class="collapse-title px-0">
              <InputLabel class="mb-4">Advanced</InputLabel>
            </div>
            <div class="collapse-content">
              <Field
                name="machine.flake"
                validate={[required("This field is required")]}
              >
                {(field, props) => (
                  <>
                    <TextInput
                      inputProps={props}
                      label="Source (flake URL)"
                      value={String(field.value)}
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
                      inputProps={props}
                      label="Image Name (attribute name)"
                      value={String(field.value)}
                      error={field.error}
                      required
                    />
                  </>
                )}
              </Field>
              <FieldLayout
                label={
                  <InputLabel help="Computed reference">Source Url</InputLabel>
                }
                field={
                  <InputLabel>
                    {getValue(formStore, "machine.flake") +
                      "#" +
                      getValue(formStore, "machine.devicePath")}
                  </InputLabel>
                }
              />
              <hr class="mb-6"></hr>

              <Field
                name="language"
                validate={[required("This field is required")]}
              >
                {(field, props) => (
                  <>
                    <SelectInput
                      selectProps={props}
                      label="Language"
                      value={String(field.value)}
                      error={field.error}
                      required
                      loading={langQuery.isLoading}
                      options={[
                        {
                          label: "en_US.UTF-8",
                          value: "en_US.UTF-8",
                        },
                        ...(langQuery.data?.map((lang) => ({
                          label: lang,
                          value: lang,
                        })) || []),
                      ]}
                    />
                  </>
                )}
              </Field>

              <Field
                name="keymap"
                validate={[required("This field is required")]}
              >
                {(field, props) => (
                  <>
                    <SelectInput
                      selectProps={props}
                      label="Keymap"
                      value={String(field.value)}
                      error={field.error}
                      required
                      loading={keymapQuery.isLoading}
                      options={[
                        {
                          label: "en",
                          value: "en",
                        },
                        ...(keymapQuery.data?.map((keymap) => ({
                          label: keymap,
                          value: keymap,
                        })) || []),
                      ]}
                    />
                  </>
                )}
              </Field>
            </div>
          </div>

          <hr></hr>
          <div class="mt-2 flex justify-end pt-2">
            <Button
              class="self-end"
              type="submit"
              disabled={formStore.submitting}
              startIcon={
                formStore.submitting ? (
                  <Icon icon="Load" />
                ) : (
                  <Icon icon="Flash" />
                )
              }
            >
              {formStore.submitting ? "Flashing..." : "Flash Installer"}
            </Button>
          </div>
        </Form>
      </div>
    </>
  );
};
