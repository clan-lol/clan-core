import { For, Match, Switch, createEffect, type Component } from "solid-js";
import { useCountContext } from "../../Config";
import { route } from "@/src/App";

export const MachineListView: Component = () => {
  const [{ machines, loading }, { getMachines }] = useCountContext();

  createEffect(() => {
    if (route() === "machines") getMachines();
  });
  return (
    <div class="max-w-screen-lg">
      <div class="tooltip" data-tip="Refresh ">
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
        <Match when={!loading() && machines().length === 0}>
          No machines found
        </Match>
        <Match when={!loading()}>
          <ul>
            <For each={machines()}>
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
