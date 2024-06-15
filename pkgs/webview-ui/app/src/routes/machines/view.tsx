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
import toast from "solid-toast";
import { MachineListItem } from "@/src/components/MachineListItem";

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
      toast.success("Machines loaded");
    }
    if (response?.status === "error") {
      setData([]);
      console.error(response.errors);
      toast.error("Error loading machines");
      response.errors.forEach((error) =>
        toast.error(
          `${error.message}: ${error.description} From ${error.location}`
        )
      );
    }
  });

  return (
    <div class="max-w-screen-lg">
      <div class="tooltip" data-tip="Open Clan">
        <button
          class="btn btn-ghost"
          onClick={() =>
            pyApi.open_file.dispatch({
              file_request: {
                title: "Open Clan",
                mode: "select_folder",
              },
            })
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
              {(entry) => <MachineListItem name={entry} />}
            </For>
          </ul>
        </Match>
      </Switch>
    </div>
  );
};
