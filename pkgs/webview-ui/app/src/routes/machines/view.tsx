import {
  For,
  Match,
  Show,
  Switch,
  createEffect,
  createSignal,
  type Component,
} from "solid-js";
import { activeURI, route, setActiveURI, setRoute } from "@/src/App";
import { OperationResponse, callApi, pyApi } from "@/src/api";
import toast from "solid-toast";
import { MachineListItem } from "@/src/components/MachineListItem";

// type FilesModel = Extract<
//   OperationResponse<"get_directory">,
//   { status: "success" }
// >["data"]["files"];

// type ServiceModel = Extract<
//   OperationResponse<"show_mdns">,
//   { status: "success" }
// >["data"]["services"];

type MachinesModel = Extract<
  OperationResponse<"list_machines">,
  { status: "success" }
>["data"];

// pyApi.open_file.receive((r) => {
//   if (r.op_key === "open_clan") {
//     console.log(r);
//     if (r.status === "error") return console.error(r.errors);

//     if (r.data) {
//       setCurrClanURI(r.data);
//     }
//   }
// });

export const MachineListView: Component = () => {
  // const [files, setFiles] = createSignal<FilesModel>([]);

  // pyApi.get_directory.receive((r) => {
  //   const { status } = r;
  //   if (status === "error") return console.error(r.errors);
  //   setFiles(r.data.files);
  // });

  // const [services, setServices] = createSignal<ServiceModel>();
  // pyApi.show_mdns.receive((r) => {
  //   const { status } = r;
  //   if (status === "error") return console.error(r.errors);
  //   setServices(r.data.services);
  // });

  const [machines, setMachines] = createSignal<MachinesModel>({});
  const [loading, setLoading] = createSignal<boolean>(false);

  const listMachines = async () => {
    const uri = activeURI();
    if (!uri) {
      return;
    }
    setLoading(true);
    const response = await callApi("list_machines", {
      flake_url: uri,
    });
    setLoading(false);
    if (response.status === "success") {
      setMachines(response.data);
    }
  };

  createEffect(() => {
    if (route() === "machines") listMachines();
  });

  const unpackedMachines = () => Object.entries(machines());

  return (
    <div class="max-w-screen-lg">
      <div class="tooltip tooltip-bottom" data-tip="Open Clan"></div>
      <div class="tooltip tooltip-bottom" data-tip="Refresh">
        <button class="btn btn-ghost" onClick={() => listMachines()}>
          <span class="material-icons ">refresh</span>
        </button>
      </div>
      <div class="tooltip tooltip-bottom" data-tip="Create machine">
        <button class="btn btn-ghost" onClick={() => setRoute("machines/add")}>
          <span class="material-icons ">add</span>
        </button>
      </div>
      {/* <Show when={services()}>
        {(services) => (
          <For each={Object.values(services())}>
            {(service) => (
              <div class="rounded-lg bg-white p-5 shadow-lg">
                <h2 class="mb-2 text-xl font-semibold">{service.name}</h2>
                <p>
                  <span class="font-bold">Interface:</span>
                  {service.interface}
                </p>
                <p>
                  <span class="font-bold">Protocol:</span>
                  {service.protocol}
                </p>
                <p>
                  <span class="font-bold">Name</span>
                  {service.name}
                </p>
                <p>
                  <span class="font-bold">Type:</span>
                  {service.type_}
                </p>
                <p>
                  <span class="font-bold">Domain:</span>
                  {service.domain}
                </p>
                <p>
                  <span class="font-bold">Host:</span>
                  {service.host}
                </p>
                <p>
                  <span class="font-bold">IP:</span>
                  {service.ip}
                </p>
                <p>
                  <span class="font-bold">Port:</span>
                  {service.port}
                </p>
                <p>
                  <span class="font-bold">TXT:</span>
                  {service.txt}
                </p>
              </div>
            )}
          </For>
        )}
      </Show> */}
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
        <Match when={!loading() && unpackedMachines().length === 0}>
          No machines found
        </Match>
        <Match when={!loading()}>
          <ul>
            <For each={unpackedMachines()}>
              {([name, info]) => <MachineListItem name={name} info={info} />}
            </For>
          </ul>
        </Match>
      </Switch>
    </div>
  );
};
