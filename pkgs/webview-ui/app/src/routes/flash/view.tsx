import { callApi } from "@/src/api";
import { Button } from "@/src/components/button";
// Icon is used in CustomFileField, ensure it's available or remove if not needed there
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
  getValues,
} from "@modular-forms/solid";
import { createQuery } from "@tanstack/solid-query";
import { createEffect, createSignal, For, Show } from "solid-js"; // For, Show might not be needed directly here now
import toast from "solid-toast";
import { FieldLayout } from "@/src/Form/fields/layout";
import { InputLabel } from "@/src/components/inputBase";
import { Modal } from "@/src/components/modal";
import Fieldset from "@/src/Form/fieldset"; // Still used for other fieldsets
import Accordion from "@/src/components/accordion";

// Import the new generic component
import {
  FileSelectorField,
  type FileDialogOptions,
} from "@/src/components/fileSelect"; // Adjust path

interface Wifi extends FieldValues {
  ssid: string;
  password: string;
}

export interface FlashFormValues extends FieldValues {
  machine: {
    devicePath: string;
    flake: string;
  };
  disk: string;
  language: string;
  keymap: string;
  wifi: Wifi[];
  sshKeys: File[]; // This field will use CustomFileField
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
      // sshKeys: [] // Initial value for sshKeys (optional, modular-forms handles undefined)
    },
  });

  /* ==== WIFI NETWORK (logic remains the same) ==== */
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
  // Define the options for the SSH key file dialog
  const sshKeyDialogOptions: FileDialogOptions = {
    title: "Select SSH Public Key(s)",
    filters: { patterns: ["*.pub"] },
    initial_folder: "~/.ssh",
  };

  const [confirmOpen, setConfirmOpen] = createSignal(false);
  const [isFlashing, setFlashing] = createSignal(false);

  const handleSubmit = (values: FlashFormValues) => {
    // Basic check for sshKeys, could add to modular-forms validation
    if (!values.sshKeys || values.sshKeys.length === 0) {
      toast.error("Please select at least one SSH key.");
      return;
    }
    setConfirmOpen(true);
  };

  const handleConfirm = async () => {
    const values = getValues(formStore) as FlashFormValues;
    // Additional check, though handleSubmit should catch it
    if (!values.sshKeys || values.sshKeys.length === 0) {
      toast.error("SSH keys are missing. Cannot proceed with flash.");
      setConfirmOpen(false);
      return;
    }
    setFlashing(true);
    console.log("Confirmed flash:", values);
    try {
      await toast.promise(
        callApi("flash_machine", {
          machine: {
            name: values.machine.devicePath,
            flake: {
              identifier: values.machine.flake,
            },
          },
          mode: "format",
          disks: [{ name: "main", device: values.disk }],
          system_config: {
            language: values.language,
            keymap: values.keymap,
            // Ensure sshKeys is correctly mapped (File[] to string[])
            ssh_keys_path: values.sshKeys.map((file) => file.name),
          },
          dry_run: false,
          write_efi_boot_entries: false,
          debug: false,
          graphical: true,
        }),
        {
          error: (errors) => `Error flashing disk: ${errors}`,
          loading: "Flashing ... This may take up to 15minutes.",
          success: "Disk flashed successfully",
        },
      );
    } catch (error) {
      toast.error(`Error could not flash disk: ${error}`);
    } finally {
      setFlashing(false);
    }
    setConfirmOpen(false);
  };

  return (
    <>
      <Header title="Flash installer" />
      <Modal
        open={confirmOpen() || isFlashing()}
        handleClose={() => !isFlashing() && setConfirmOpen(false)}
        title="Confirm"
      >
        {/* ... Modal content as before ... */}
        <div class="flex flex-col gap-4 p-4">
          <div class="flex flex-col justify-between rounded-sm border p-4 align-middle text-red-900 border-def-2">
            <Typography
              hierarchy="label"
              weight="medium"
              size="default"
              class="flex-wrap break-words pr-4"
            >
              Warning: All data will be lost.
            </Typography>
            <Typography
              hierarchy="label"
              weight="bold"
              size="default"
              class="flex-wrap break-words pr-4"
            >
              Selected disk: '{getValue(formStore, "disk")}'
            </Typography>
          </div>
          <div class="flex w-full justify-between">
            <Button
              disabled={isFlashing()}
              variant="light"
              onClick={() => setConfirmOpen(false)}
            >
              Cancel
            </Button>
            <Button disabled={isFlashing()} onClick={handleConfirm}>
              Confirm
            </Button>
          </div>
        </div>
      </Modal>
      <div class="w-full self-stretch p-8">
        <Form
          onSubmit={handleSubmit}
          class="mx-auto flex w-full max-w-2xl flex-col gap-y-6"
        >
          <FileSelectorField
            Field={Field}
            name="sshKeys" // Corresponds to FlashFormValues.sshKeys
            label="Authorized SSH Keys"
            description="Provide your SSH public key(s) for secure, passwordless connections. (.pub files)"
            multiple={true} // Allow multiple SSH keys
            fileDialogOptions={sshKeyDialogOptions}
            // You could add custom validation via modular-forms 'validate' prop on CustomFileField if needed
            // e.g. validate={[required("At least one SSH key is required.")]}
            // This would require CustomFileField to accept and pass `validate` to its internal `Field`.
          />

          <Fieldset legend="General">
            <Field name="disk" validate={[required("This field is required")]}>
              {(field, props) => (
                <>
                  <SelectInput
                    loading={deviceQuery.isFetching}
                    selectProps={props}
                    label="Flash Disk"
                    labelProps={{
                      labelAction: (
                        <Button
                          disabled={isFlashing()}
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
                    placeholder="Select a drive"
                    options={
                      deviceQuery.data?.blockdevices.map((d) => ({
                        value: d.path,
                        label: `${d.path} -- ${d.size} bytes`,
                      })) || []
                    }
                  />
                </>
              )}
            </Field>
          </Fieldset>

          <Fieldset legend="Network Settings">
            {/* ... Network settings as before ... */}
            <FieldLayout
              label={<InputLabel>Networks</InputLabel>}
              field={
                <div class="flex w-full justify-end">
                  <Button
                    type="button"
                    size="s"
                    variant="light"
                    onClick={addWifiNetwork}
                    startIcon={<Icon size={12} icon="Plus" />}
                  >
                    WiFi Network
                  </Button>
                </div>
              }
            />
            {/* TODO: You would render the actual WiFi input fields here using a <For> loop over wifiNetworks() signal */}
          </Fieldset>

          <Accordion title="Advanced">
            <Fieldset>
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
            </Fieldset>
          </Accordion>

          <div class="mt-2 flex justify-end pt-2">
            <Button
              class="self-end"
              type="submit"
              disabled={formStore.submitting || isFlashing()}
              startIcon={
                formStore.submitting || isFlashing() ? (
                  <Icon icon="Load" />
                ) : (
                  <Icon icon="Flash" />
                )
              }
            >
              {formStore.submitting || isFlashing()
                ? "Flashing..."
                : "Flash Installer"}
            </Button>
          </div>
        </Form>
      </div>
    </>
  );
};
