import { createSignal, createEffect, JSX, Show } from "solid-js";
import { useQuery } from "@tanstack/solid-query";
import { callApi, SuccessQuery } from "@/src/api";
import { TextInput } from "@/src/Form/fields/TextInput";
import { SelectInput } from "@/src/Form/fields/Select";
import { FileInput } from "@/src/components/FileInput";
import { FieldLayout } from "@/src/Form/fields/layout";
import { InputLabel } from "@/src/components/inputBase";
import Icon from "@/src/components/icon";
import { Loader } from "@/src/components/v2/Loader/Loader";
import { Button } from "@/src/components/v2/Button/Button";
import Accordion from "@/src/components/accordion";

// Export the API types for use in other components
export type { RemoteData, Machine, RemoteDataSource };

type RemoteDataSource = SuccessQuery<"get_host">["data"];
type MachineListData = SuccessQuery<"list_machines">["data"][string];
type RemoteData = NonNullable<RemoteDataSource>["data"];

// Machine type with flake for API calls
interface Machine {
  name: string;
  flake: {
    identifier: string;
  };
}

interface CheckboxInputProps {
  label: JSX.Element;
  value: boolean;
  onInput: (value: boolean) => void;
  help?: string;
  class?: string;
  disabled?: boolean;
}

function CheckboxInput(props: CheckboxInputProps) {
  return (
    <FieldLayout
      label={
        <InputLabel class="col-span-2" help={props.help}>
          {props.label}
        </InputLabel>
      }
      field={
        <div class="col-span-10 flex items-center">
          <input
            type="checkbox"
            checked={props.value}
            onChange={(e) => props.onInput(e.currentTarget.checked)}
            disabled={props.disabled}
            class="size-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
        </div>
      }
      class={props.class}
    />
  );
}

interface KeyValueInputProps {
  label: JSX.Element;
  value: Record<string, string>;
  onInput: (value: Record<string, string>) => void;
  help?: string;
  class?: string;
  disabled?: boolean;
}

function KeyValueInput(props: KeyValueInputProps) {
  const [newKey, setNewKey] = createSignal("");
  const [newValue, setNewValue] = createSignal("");

  const addPair = () => {
    const key = newKey().trim();
    const value = newValue().trim();
    if (key && value) {
      props.onInput({ ...props.value, [key]: value });
      setNewKey("");
      setNewValue("");
    }
  };

  const removePair = (key: string) => {
    const { [key]: _, ...newObj } = props.value;
    props.onInput(newObj);
  };

  return (
    <FieldLayout
      label={
        <InputLabel class="col-span-2" help={props.help}>
          {props.label}
        </InputLabel>
      }
      field={
        <div class="col-span-10 space-y-2">
          {/* Existing pairs */}
          {Object.entries(props.value).map(([key, value]) => (
            <div class="flex items-center gap-2">
              <span class="text-sm font-medium">{key}:</span>
              <span class="text-sm">{value}</span>
              <button
                type="button"
                onClick={() => removePair(key)}
                class="text-red-600 hover:text-red-800"
                disabled={props.disabled}
              >
                ×
              </button>
            </div>
          ))}

          {/* Add new pair */}
          <div class="flex gap-2">
            <input
              type="text"
              placeholder="Key"
              value={newKey()}
              onInput={(e) => setNewKey(e.currentTarget.value)}
              disabled={props.disabled}
              class="flex-1 rounded border border-gray-300 px-2 py-1 text-sm"
            />
            <input
              type="text"
              placeholder="Value"
              value={newValue()}
              onInput={(e) => setNewValue(e.currentTarget.value)}
              disabled={props.disabled}
              class="flex-1 rounded border border-gray-300 px-2 py-1 text-sm"
            />
            <button
              type="button"
              onClick={addPair}
              disabled={
                props.disabled || !newKey().trim() || !newValue().trim()
              }
              class="rounded bg-blue-600 px-3 py-1 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
            >
              Add
            </button>
          </div>
        </div>
      }
      class={props.class}
    />
  );
}

interface RemoteFormProps {
  onInput?: (value: RemoteData) => void;
  machine: Machine;
  field?: "targetHost" | "buildHost";
  disabled?: boolean;
  // Optional query function for testing/mocking
  queryFn?: (params: {
    name: string;
    flake: {
      identifier: string;
      hash?: string | null;
      store_path?: string | null;
    };
    field: string;
  }) => Promise<RemoteDataSource | null>;
  // Optional save handler for custom save behavior (e.g., in Storybook)
  onSave?: (data: RemoteData) => void | Promise<void>;
  // Show/hide save button
  showSave?: boolean;
}

export function RemoteForm(props: RemoteFormProps) {
  const [isLocked, setIsLocked] = createSignal(true);
  const [source, setSource] = createSignal<"inventory" | "nix_machine" | null>(
    null,
  );
  const [privateKeyFile, setPrivateKeyFile] = createSignal<File | undefined>();
  const [formData, setFormData] = createSignal<RemoteData | null>(null);
  const [isSaving, setIsSaving] = createSignal(false);

  // Query host data when machine is provided
  const hostQuery = useQuery(() => ({
    queryKey: [
      "get_host",
      props.machine,
      props.queryFn,
      props.machine?.name,
      props.machine?.flake,
      props.field || "targetHost",
    ],
    queryFn: async () => {
      if (!props.machine) return null;

      // Use custom query function if provided (for testing/mocking)
      if (props.queryFn) {
        return props.queryFn({
          name: props.machine.name,
          flake: props.machine.flake,
          field: props.field || "targetHost",
        });
      }

      const result = await callApi(
        "get_host",
        {
          name: props.machine.name,
          flake: props.machine.flake,
          field: props.field || "targetHost",
        },
        {
          logging: {
            group: { name: props.machine.name, flake: props.machine.flake },
          },
        },
      ).promise;

      if (result.status === "error")
        throw new Error("Failed to fetch host data");
      return result.data;
    },
    enabled: !!props.machine,
  }));

  // Update form data and lock state when host data is loaded
  createEffect(() => {
    const hostData = hostQuery.data;
    if (hostData?.data) {
      setSource(hostData.source);
      setIsLocked(hostData.source === "nix_machine");
      setFormData(hostData.data);
      props.onInput?.(hostData.data);
    }
  });

  const isFormDisabled = () =>
    props.disabled || (source() === "nix_machine" && isLocked());
  const computedDisabled = isFormDisabled();

  const updateFormData = (updates: Partial<RemoteData>) => {
    const current = formData();
    if (current) {
      const updated = { ...current, ...updates };
      setFormData(updated);
      props.onInput?.(updated);
    }
  };

  const handleSave = async () => {
    const data = formData();
    if (!data || isSaving()) return;

    setIsSaving(true);
    try {
      if (props.onSave) {
        await props.onSave(data);
      } else {
        // Default save behavior - could be extended with API call
        console.log("Saving remote data:", data);
      }
    } catch (error) {
      console.error("Error saving remote data:", error);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div class="space-y-4">
      <Show when={hostQuery.isLoading}>
        <div class="flex justify-center p-8">
          <Loader />
        </div>
      </Show>

      <Show when={!hostQuery.isLoading && formData()}>
        {/* Lock header for nix_machine source */}
        <Show when={source() === "nix_machine"}>
          <div class="flex items-center justify-between rounded-md border border-amber-200 bg-amber-50 p-3">
            <div class="flex items-center gap-2">
              <Icon icon="Warning" class="size-5 text-amber-600" />
              <span class="text-sm font-medium text-amber-800">
                Configuration managed by Nix
              </span>
            </div>
            <button
              type="button"
              onClick={() => setIsLocked(!isLocked())}
              class="flex items-center gap-1 rounded px-2 py-1 text-xs font-medium text-amber-700 hover:bg-amber-100"
            >
              <Icon icon={isLocked() ? "Settings" : "Edit"} class="size-3" />
              {isLocked() ? "Unlock to edit" : "Lock"}
            </button>
          </div>
        </Show>

        {/* Basic Connection Fields - Always Visible */}
        <TextInput
          label="User"
          value={formData()?.user || ""}
          inputProps={{
            onInput: (e) => updateFormData({ user: e.currentTarget.value }),
          }}
          placeholder="username"
          required
          disabled={computedDisabled}
          help="Username to connect as on the remote server"
        />
        <TextInput
          label="Address"
          value={formData()?.address || ""}
          inputProps={{
            onInput: (e) => updateFormData({ address: e.currentTarget.value }),
          }}
          placeholder="hostname or IP address"
          required
          disabled={computedDisabled}
          help="The hostname or IP address of the remote server"
        />

        {/* Advanced Options - Collapsed by Default */}
        <Accordion title="Advanced Options" class="mt-6">
          <div class="space-y-4 pt-2">
            <TextInput
              label="Port"
              value={formData()?.port?.toString() || ""}
              inputProps={{
                type: "number",
                onInput: (e) => {
                  const value = e.currentTarget.value;
                  updateFormData({
                    port: value ? parseInt(value, 10) : undefined,
                  });
                },
              }}
              placeholder="22"
              disabled={computedDisabled}
              help="SSH port (defaults to 22 if not specified)"
            />

            <SelectInput
              label="Host Key Check"
              value={formData()?.host_key_check || "ask"}
              options={[
                { value: "ask", label: "Ask" },
                { value: "none", label: "None" },
                { value: "strict", label: "Strict" },
                { value: "tofu", label: "Trust on First Use" },
              ]}
              disabled={computedDisabled}
              helperText="How to handle host key verification"
            />
            <Show when={typeof window !== "undefined"}>
              <FieldLayout
                label={
                  <InputLabel
                    class="col-span-2"
                    help="SSH private key file for authentication"
                  >
                    Private Key
                  </InputLabel>
                }
                field={
                  <div class="col-span-10">
                    <FileInput
                      name="private_key"
                      accept=".pem,.key,*"
                      value={privateKeyFile()}
                      onInput={(e) => {
                        const file = e.currentTarget.files?.[0];
                        setPrivateKeyFile(file);
                        updateFormData({
                          private_key: file?.name || null,
                        });
                      }}
                      onChange={() => void 0}
                      onBlur={() => void 0}
                      onClick={() => void 0}
                      ref={() => void 0}
                      placeholder={<>Click to select private key file</>}
                      class="w-full"
                    />
                  </div>
                }
              />
            </Show>

            <CheckboxInput
              label="Forward Agent"
              value={formData()?.forward_agent || false}
              onInput={(value) => updateFormData({ forward_agent: value })}
              disabled={computedDisabled}
              help="Enable SSH agent forwarding"
            />

            <KeyValueInput
              label="SSH Options"
              value={formData()?.ssh_options || {}}
              onInput={(value) => updateFormData({ ssh_options: value })}
              disabled={computedDisabled}
              help="Additional SSH options as key-value pairs"
            />

            <CheckboxInput
              label="Tor SOCKS"
              value={formData()?.tor_socks || false}
              onInput={(value) => updateFormData({ tor_socks: value })}
              disabled={computedDisabled}
              help="Use Tor SOCKS proxy for SSH connection"
            />
          </div>
        </Accordion>

        {/* Save Button */}
        <Show when={props.showSave !== false}>
          <div class="flex justify-end pt-4">
            <Button
              onClick={handleSave}
              disabled={computedDisabled || isSaving()}
              class="min-w-24"
            >
              {isSaving() ? "Saving..." : "Save"}
            </Button>
          </div>
        </Show>
      </Show>
    </div>
  );
}
