import { callApi } from "@/src/api";
import { activeURI } from "@/src/App";
import { useParams } from "@solidjs/router";
import { createQuery } from "@tanstack/solid-query";
import { createSignal, Show } from "solid-js";
import toast from "solid-toast";

export const MachineDetails = () => {
  const params = useParams();
  const query = createQuery(() => ({
    queryKey: [activeURI(), "machine", params.id],
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

  return (
    <div>
      {query.isLoading && <span class="loading loading-bars" />}
      <Show when={!query.isLoading && query.data}>
        {(data) => (
          <div class="grid grid-cols-2 gap-2 text-lg">
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
          </div>
        )}
      </Show>
    </div>
  );
};
