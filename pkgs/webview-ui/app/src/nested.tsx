import { For, Match, Switch, type Component } from "solid-js";
import { useCountContext } from "./Config";

export const Nested: Component = () => {
  const [{ machines, loading }, { getMachines }] = useCountContext();
  return (
    <div>
      <button onClick={() => getMachines()} class="btn btn-primary">
        Get machines
      </button>
      <hr />
      <Switch>
        <Match when={loading()}>Loading...</Match>
        <Match when={!loading() && machines().length === 0}>
          No machines found
        </Match>
        <Match when={!loading() && machines().length}>
          <For each={machines()}>
            {(machine, i) => (
              <li>
                {i() + 1}: {machine}
              </li>
            )}
          </For>
        </Match>
      </Switch>
    </div>
  );
};
