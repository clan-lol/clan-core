import { pyApi } from "@/src/api";
import { Match, Switch, createEffect, createSignal } from "solid-js";
import toast from "solid-toast";
import { ClanDetails, EditMetaFields } from "./clanDetails";

export const clan = () => {
  const [mode, setMode] = createSignal<"init" | "open" | "create">("init");
  const [clanDir, setClanDir] = createSignal<string | null>(null);

  createEffect(() => {
    console.log(mode());
  });
  return (
    <div>
      <Switch fallback={"invalid"}>
        <Match when={mode() === "init"}>
          <div class="flex gap-2">
            <button class="btn btn-square" onclick={() => setMode("create")}>
              <span class="material-icons">add</span>
            </button>
            <button
              class="btn btn-square"
              onclick={() => {
                pyApi.open_file.dispatch({
                  file_request: {
                    mode: "select_folder",
                    title: "Open Clan",
                  },
                });
                pyApi.open_file.receive((r) => {
                  // There are two error cases to handle
                  if (r.status !== "success") {
                    console.error(r.errors);
                    toast.error("Error opening clan");
                    return;
                  }
                  // User didn't select anything
                  if (!r.data) {
                    setMode("init");
                    return;
                  }

                  setClanDir(r.data);
                  setMode("open");
                });
              }}
            >
              <span class="material-icons">folder_open</span>
            </button>
          </div>
        </Match>
        <Match when={mode() === "open"}>
          <ClanDetails directory={clanDir() || ""} />
        </Match>
        <Match when={mode() === "create"}>
          <EditMetaFields
            actions={
              <div class="card-actions justify-end">
                <button
                  class="btn btn-primary"
                  onClick={() => {
                    pyApi.open_file.dispatch({
                      file_request: { mode: "save" },
                    });
                  }}
                >
                  Save
                </button>
              </div>
            }
            meta={{
              name: "New Clan",
              description: "nice description",
              icon: "select icon",
            }}
            editable
          />
        </Match>
      </Switch>
    </div>
  );
};
