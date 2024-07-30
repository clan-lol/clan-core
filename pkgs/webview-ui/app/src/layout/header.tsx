import { createQuery } from "@tanstack/solid-query";
import { activeURI, setRoute } from "../App";
import { callApi } from "../api";
import { Accessor, createEffect, Show } from "solid-js";

interface HeaderProps {
  clan_dir: Accessor<string | null>;
}
export const Header = (props: HeaderProps) => {
  const { clan_dir } = props;

  const query = createQuery(() => ({
    queryKey: [clan_dir(), "meta"],
    queryFn: async () => {
      const curr = clan_dir();
      if (curr) {
        const result = await callApi("show_clan_meta", { uri: curr });
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
        <Show when={!query.isFetching && query.data}>
          {(meta) => (
            <div class="tooltip tooltip-right" data-tip={activeURI()}>
              <div class="avatar placeholder online mx-4">
                <div class="w-10 rounded-full bg-slate-700 text-3xl text-neutral-content">
                  {meta().name.slice(0, 1)}
                </div>
              </div>
            </div>
          )}
        </Show>
        <span class="flex flex-col">
          <Show when={!query.isFetching && query.data}>
            {(meta) => [
              <span class="text-primary">{meta().name}</span>,
              <span class="text-neutral">{meta()?.description}</span>,
            ]}
          </Show>
        </span>
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
