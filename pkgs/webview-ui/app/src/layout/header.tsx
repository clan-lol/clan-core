import { activeURI, setRoute } from "../App";

export const Header = () => {
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
        <a class="text-xl">{activeURI()}</a>
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
