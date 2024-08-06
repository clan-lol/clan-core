import { type Component, createEffect, For, Match, Switch } from "solid-js";
import { activeURI, setRoute } from "@/src/App";
import { callApi, OperationResponse } from "@/src/api";
import toast from "solid-toast";
import { MachineListItem } from "@/src/components/MachineListItem";
import { createQuery } from "@tanstack/solid-query";

type MachinesModel = Extract<
  OperationResponse<"list_inventory_machines">,
  { status: "success" }
>["data"];

export const MachineListView: Component = () => {
  const {
    data: nixosMachines,
    isFetching: isLoadingNixos,
    refetch: refetchNixos,
  } = createQuery<string[]>(() => ({
    queryKey: [activeURI(), "list_nixos_machines"],
    queryFn: async () => {
      const uri = activeURI();
      if (uri) {
        const response = await callApi("list_nixos_machines", {
          flake_url: uri,
        });
        if (response.status === "error") {
          toast.error("Failed to fetch data");
        } else {
          return response.data;
        }
      }
      return [];
    },
    staleTime: 1000 * 60 * 5,
  }));
  const {
    data: inventoryMachines,
    isFetching: isLoadingInventory,
    refetch: refetchInventory,
  } = createQuery<MachinesModel>(() => ({
    queryKey: [activeURI(), "list_inventory_machines"],
    initialData: {},
    queryFn: async () => {
      const uri = activeURI();
      if (uri) {
        const response = await callApi("list_inventory_machines", {
          flake_url: uri,
        });
        if (response.status === "error") {
          toast.error("Failed to fetch data");
        } else {
          return response.data;
        }
      }
      return {};
    },
    staleTime: 1000 * 60 * 5,
  }));

  const refresh = async () => {
    refetchInventory();
    refetchNixos();
  };

  const unpackedMachines = () => Object.entries(inventoryMachines);
  const nixOnlyMachines = () =>
    nixosMachines?.filter(
      (name) => !unpackedMachines().some(([key, machine]) => key === name),
    );

  createEffect(() => {
    console.log(nixOnlyMachines(), unpackedMachines());
  });

  return (
    <div class="max-w-screen-lg">
      <div class="tooltip tooltip-bottom" data-tip="Open Clan"></div>
      <div class="tooltip tooltip-bottom" data-tip="Refresh">
        <button class="btn btn-ghost" onClick={() => refresh()}>
          <span class="material-icons ">refresh</span>
        </button>
      </div>
      <div class="tooltip tooltip-bottom" data-tip="Create machine">
        <button class="btn btn-ghost" onClick={() => setRoute("machines/add")}>
          <span class="material-icons ">add</span>
        </button>
      </div>
      <Switch>
        <Match when={isLoadingInventory}>
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
        <Match
          when={
            !isLoadingInventory &&
            unpackedMachines().length === 0 &&
            nixOnlyMachines()?.length === 0
          }
        >
          No machines found
        </Match>
        <Match when={!isLoadingInventory}>
          <ul>
            <For each={unpackedMachines()}>
              {([name, info]) => <MachineListItem name={name} info={info} />}
            </For>
            <For each={nixOnlyMachines()}>
              {(name) => <MachineListItem name={name} />}
            </For>
          </ul>
        </Match>
      </Switch>
    </div>
  );
};
