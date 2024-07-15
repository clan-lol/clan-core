import { createQuery } from "@tanstack/solid-query";
import { activeURI, setRoute } from "../App";
import { callApi } from "../api";
import { Show } from "solid-js";

export const Header = () => {
  const { isLoading, data } = createQuery(() => ({
    queryKey: [`${activeURI()}:meta`],
    queryFn: async () => {
      const currUri = activeURI();
      if (currUri) {
        const result = await callApi("show_clan_meta", { uri: currUri });
        if (result.status === "error") throw new Error("Failed to fetch data");
        return result.data;
      }
    },
  }));

  return (
    <div class="navbar bg-base-100">
      <div class="flex-none">
        <span class="tooltip tooltip-bottom" data-tip="Menu">
          <label
            class="btn btn-square btn-ghost drawer-button"
            for="toplevel-drawer"
          >
            <span class="material-icons">menu</span>
          </label>
        </span>
      </div>
      <div class="flex-1">
        <div class="tooltip tooltip-right" data-tip={data?.name || activeURI()}>
          <div class="avatar placeholder online mx-4">
            <div class="w-10 rounded-full bg-slate-700 text-neutral-content">
              <span class="text-xl">C</span>
              <Show when={data?.name}>
                {(name) => <span class="text-xl">{name()}</span>}
              </Show>
            </div>
          </div>
        </div>
      </div>
      <div class="flex-none">
        <span class="tooltip tooltip-bottom" data-tip="Settings">
          <button class="link" onClick={() => setRoute("settings")}>
            <span class="material-icons">settings</span>
          </button>
        </span>
      </div>
    </div>
  );
};
