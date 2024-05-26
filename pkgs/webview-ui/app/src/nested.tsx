import { For, Match, Switch, createEffect, type Component } from "solid-js";
import { useCountContext } from "./Config";

export const Nested: Component = () => {
  const [{ machines, loading }, { getMachines }] = useCountContext();

  const list = () => Object.values(machines());

  createEffect(() => {
    console.log("1", list());
  });
  createEffect(() => {
    console.log("2", machines());
  });
  return (
    <div>
      <button onClick={() => getMachines()} class="btn btn-primary">
        Get machines
      </button>
      <div></div>
      <Switch>
        <Match when={loading()}>Loading...</Match>
        <Match when={!loading() && Object.entries(machines()).length === 0}>
          No machines found
        </Match>
        <Match when={!loading()}>
          <For each={list()}>
            {(entry, i) => (
              <li>
                {i() + 1}: {entry.machine_name}{" "}
                {entry.machine_description || "No description"}
              </li>
            )}
          </For>
        </Match>
      </Switch>
    </div>
  );
};
