import {
  type Component,
  createSignal,
  For,
  Match,
  Show,
  Switch,
} from "solid-js";
import { activeURI } from "@/src/App";
import { callApi, OperationResponse } from "@/src/api";
import toast from "solid-toast";
import { MachineListItem } from "@/src/components/MachineListItem";
import { createQuery, useQueryClient } from "@tanstack/solid-query";
import { useNavigate } from "@solidjs/router";
import { Button } from "@/src/components/button";
import Icon from "@/src/components/icon";
import { Header } from "@/src/layout/header";
import { makePersisted } from "@solid-primitives/storage";

type MachinesModel = Extract<
  OperationResponse<"list_inventory_machines">,
  { status: "success" }
>["data"];

export interface Filter {
  tags: string[];
}

export const MachineListView: Component = () => {
  const queryClient = useQueryClient();

  const [filter, setFilter] = createSignal<Filter>({ tags: [] });

  const inventoryQuery = createQuery<MachinesModel>(() => ({
    queryKey: [activeURI(), "list_inventory_machines"],
    placeholderData: {},
    enabled: !!activeURI(),
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
  }));

  const refresh = async () => {
    queryClient.invalidateQueries({
      // Invalidates the cache for of all types of machine list at once
      queryKey: [activeURI(), "list_machines"],
    });
  };

  const inventoryMachines = () =>
    Object.entries(inventoryQuery.data || {}).filter((e) => {
      const hasAllTags = filter().tags.every((tag) => e[1].tags?.includes(tag));

      return hasAllTags;
    });
  const navigate = useNavigate();

  const [view, setView] = makePersisted(createSignal<"list" | "grid">("list"), {
    name: "machines_view",
    storage: localStorage,
  });
  return (
    <>
      <Header
        title="Your Machines"
        toolbar={
          <>
            <span class="tooltip tooltip-bottom" data-tip="Reload">
              <Button
                variant="light"
                size="s"
                onClick={() => refresh()}
                startIcon={<Icon icon="Update" />}
              ></Button>
            </span>

            <div class="border border-def-3">
              <span class="tooltip tooltip-bottom" data-tip="List View">
                <Button
                  onclick={() => setView("list")}
                  variant={view() == "list" ? "dark" : "light"}
                  size="s"
                  startIcon={<Icon icon="List" />}
                ></Button>
              </span>
              <span class="tooltip tooltip-bottom" data-tip="Grid View">
                <Button
                  onclick={() => setView("grid")}
                  variant={view() == "grid" ? "dark" : "light"}
                  size="s"
                  startIcon={<Icon icon="Grid" />}
                ></Button>
              </span>
            </div>
            <span class="tooltip tooltip-bottom" data-tip="New Machine">
              <Button
                onClick={() => navigate("create")}
                size="s"
                variant="light"
                startIcon={<Icon icon="Plus" />}
              >
                New Machine
              </Button>
            </span>
          </>
        }
      />
      <div>
        <div class="my-1 flex w-full gap-2 p-2">
          <div class="size-6 p-1">
            <Icon icon="Filter" />
          </div>
          <For each={filter().tags.sort()}>
            {(tag) => (
              <button
                type="button"
                onClick={() =>
                  setFilter((prev) => {
                    return {
                      ...prev,
                      tags: prev.tags.filter((t) => t !== tag),
                    };
                  })
                }
              >
                <span class="rounded-full px-3 py-1 bg-inv-4 fg-inv-1">
                  {tag}
                </span>
              </button>
            )}
          </For>
        </div>
        {/* </Show> */}
        <Switch>
          <Match when={inventoryQuery.isLoading}>
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
            when={!inventoryQuery.isLoading && inventoryMachines().length === 0}
          >
            <div class="mt-8 flex w-full flex-col items-center justify-center gap-2">
              <span class="text-lg text-neutral">
                No machines defined yet. Click below to define one.
              </span>
              <Button
                variant="light"
                class="size-28 overflow-hidden p-2"
                onClick={() => navigate("/machines/create")}
              >
                <span class="material-icons text-6xl font-light">add</span>
              </Button>
            </div>
          </Match>
          <Match when={!inventoryQuery.isLoading}>
            <div
              class="my-4 flex flex-wrap gap-6 px-3 py-2"
              classList={{
                "flex-col": view() === "list",
                "": view() === "grid",
              }}
            >
              <For each={inventoryMachines()}>
                {([name, info]) => (
                  <MachineListItem
                    name={name}
                    info={info}
                    setFilter={setFilter}
                  />
                )}
              </For>
            </div>
          </Match>
        </Switch>
      </div>
    </>
  );
};
