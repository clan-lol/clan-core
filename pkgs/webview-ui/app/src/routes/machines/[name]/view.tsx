import { callApi } from "@/src/api";
import { activeURI } from "@/src/App";
import { SelectInput } from "@/src/components/SelectInput";
import { createForm } from "@modular-forms/solid";
import { useParams } from "@solidjs/router";
import { createQuery } from "@tanstack/solid-query";
import { createSignal, For, Show } from "solid-js";
import toast from "solid-toast";

type InstallForm = {
  disk: string;
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

  const [sshKey, setSshKey] = createSignal<string>();

  const [formStore, { Form, Field }] = createForm<InstallForm>({});
  const handleSubmit = async (values: InstallForm) => {
    return null;
  };

  const targetHost = () => query?.data?.machine.deploy.targetHost;
  const remoteDiskQuery = createQuery(() => ({
    queryKey: [activeURI(), "machine", targetHost(), "show_block_devices"],
    queryFn: async () => {
      const curr = activeURI();
      if (curr) {
        const result = await callApi("show_block_devices", {
          options: {
            hostname: targetHost(),
            keyfile: sshKey(),
          },
        });
        if (result.status === "error") throw new Error("Failed to fetch data");
        return result.data;
      }
    },
  }));

  const onlineStatusQuery = createQuery(() => ({
    queryKey: [activeURI(), "machine", targetHost(), "check_machine_online"],
    queryFn: async () => {
      const curr = activeURI();
      if (curr) {
        const result = await callApi("check_machine_online", {
          flake_url: curr,
          machine_name: params.id,
          opts: {
            keyfile: sshKey(),
          },
        });
        if (result.status === "error") throw new Error("Failed to fetch data");
        return result.data;
      }
    },
    refetchInterval: 5000,
  }));

  return (
    <div>
      {query.isLoading && <span class="loading loading-bars" />}
      <Show when={!query.isLoading && query.data}>
        {(data) => (
          <div class="grid grid-cols-2 gap-2 text-lg">
            <Show when={onlineStatusQuery.isFetching} fallback={<span></span>}>
              <span class="loading loading-bars loading-sm justify-self-end"></span>
            </Show>
            <span
              class="badge badge-outline text-lg"
              classList={{
                "badge-primary": onlineStatusQuery.data === "Online",
              }}
            >
              {onlineStatusQuery.data}
            </span>

            <label class="justify-self-end font-light">Name</label>
            <span>{data().machine.name}</span>
            <span class="justify-self-end font-light">description</span>
            <span>{data().machine.description}</span>
            <span class="justify-self-end font-light">targetHost</span>
            <span>{data().machine.deploy.targetHost}</span>
            <div class="join col-span-2 justify-self-center">
              <button
                class="btn join-item btn-sm"
                onClick={async () => {
                  const response = await callApi("open_file", {
                    file_request: {
                      title: "Select SSH Key",
                      mode: "open_file",
                      initial_folder: "~/.ssh",
                    },
                  });
                  if (response.status === "success" && response.data) {
                    setSshKey(response.data[0]);
                  }
                }}
              >
                <span>{sshKey() || "Default ssh key"}</span>
              </button>
              <button
                disabled={!sshKey()}
                class="btn btn-accent join-item btn-sm"
                onClick={() => setSshKey(undefined)}
              >
                <span class="material-icons">close</span>
              </button>
            </div>

            <span class="justify-self-end font-light">has hw spec</span>
            <span>{data().has_hw_specs ? "Yes" : "Not yet"}</span>

            <div class="col-span-2 justify-self-center">
              <button
                class="btn btn-primary join-item btn-sm"
                onClick={async () => {
                  const curr_uri = activeURI();
                  if (!curr_uri) {
                    return;
                  }
                  if (!query.data?.machine.deploy.targetHost) {
                    return;
                  }

                  const lt = toast.loading("Generating HW spec ...");
                  const response = await callApi(
                    "generate_machine_hardware_info",
                    {
                      machine_name: params.id,
                      clan_dir: curr_uri,
                      hostname: query.data.machine.deploy.targetHost,
                    },
                  );
                  toast.dismiss(lt);

                  if (response.status === "success") {
                    toast.success("HW specification processed successfully");
                  }
                  if (response.status === "error") {
                    toast.error(
                      "Failed to generate. " + response.errors[0].message,
                    );
                  }
                  query.refetch();
                }}
              >
                Generate HW Spec
              </button>
            </div>
            <button
              class="btn self-end"
              onClick={() => remoteDiskQuery.refetch()}
            >
              Refresh remote disks
            </button>
            <Form onSubmit={handleSubmit} class="w-full">
              <Field name="disk">
                {(field, props) => (
                  <SelectInput
                    formStore={formStore}
                    selectProps={props}
                    label="Remote Disk to use"
                    value={String(field.value)}
                    error={field.error}
                    required
                    options={
                      <Show when={remoteDiskQuery.data}>
                        {(disks) => (
                          <>
                            <option disabled>
                              Select the boot disk of the remote machine
                            </option>
                            <For each={disks().blockdevices}>
                              {(dev) => (
                                <option value={dev.name}>
                                  {dev.name}
                                  {" -- "}
                                  {dev.size}
                                  {"bytes @"}
                                  {
                                    query.data?.machine.deploy.targetHost?.split(
                                      "@",
                                    )?.[1]
                                  }
                                </option>
                              )}
                            </For>
                          </>
                        )}
                      </Show>
                    }
                  />
                )}
              </Field>
            </Form>
          </div>
        )}
      </Show>
    </div>
  );
};
