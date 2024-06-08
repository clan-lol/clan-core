import {
  For,
  Match,
  Switch,
  createEffect,
  createSignal,
  type Component,
} from "solid-js";
import { useMachineContext } from "../../Config";
import { route } from "@/src/App";
import { OperationResponse, pyApi } from "@/src/api";

type FilesModel = Extract<
  OperationResponse<"get_directory">,
  { status: "success" }
>["data"]["files"];

export const MachineListView: Component = () => {
  const [{ machines, loading }, { getMachines }] = useMachineContext();

  const [files, setFiles] = createSignal<FilesModel>([]);
  pyApi.get_directory.receive((r) => {
    const { status } = r;
    if (status === "error") return console.error(r.errors);
    setFiles(r.data.files);
  });

  createEffect(() => {
    console.log(files());
  });

  const [data, setData] = createSignal<string[]>([]);
  createEffect(() => {
    if (route() === "machines") getMachines();
  });

  createEffect(() => {
    const response = machines();
    if (response?.status === "success") {
      console.log(response.data);
      setData(response.data);
    }
  });

  return (
    <div class="max-w-screen-lg">
      <div class="tooltip" data-tip="Open Clan">
        <button
          class="btn btn-ghost"
          onClick={() =>
            pyApi.get_directory.dispatch({ current_path: "/home/" })
          }
        >
          <span class="material-icons ">folder_open</span>
        </button>
      </div>
      <div class="tooltip" data-tip="Refresh">
        <button class="btn btn-ghost" onClick={() => getMachines()}>
          <span class="material-icons ">refresh</span>
        </button>
      </div>
      <Switch>
        <Match when={loading()}>
          {/* Loading skeleton */}
          <div>
            <div class="card card-side m-2 bg-base-100 shadow-lg">
              <figure class="pl-2">
                <div class="skeleton size-12"></div>
              </figure>
              <div class="card-body">
                <h2 class="card-title">
                  <div class="skeleton h-12 w-80"></div>
                </h2>
                <div class="skeleton h-8 w-72"></div>
              </div>
            </div>
          </div>
        </Match>
        <Match when={!loading() && data().length === 0}>
          No machines found
        </Match>
        <Match when={!loading()}>
          <ul>
            <For each={data()}>
              {(entry) => (
                <li>
                  <div class="card card-side m-2 bg-base-100 shadow-lg">
                    <figure class="pl-2">
                      <span class="material-icons content-center text-5xl">
                        devices_other
                      </span>
                    </figure>
                    <div class="card-body flex-row justify-between">
                      <div class="flex flex-col">
                        <h2 class="card-title">{entry}</h2>
                        {/*
                        <p
                          classList={{
                            "text-gray-400": !entry.machine_description,
                            "text-gray-600": !!entry.machine_description,
                          }}
                        >
                          {entry.machine_description || "No description"}
                        </p>
                        */}
                      </div>
                      <div>
                        <button class="btn btn-ghost">
                          <span class="material-icons">more_vert</span>
                        </button>
                      </div>
                    </div>
                  </div>
                </li>
              )}
            </For>
          </ul>
        </Match>
      </Switch>
    </div>
  );
};
