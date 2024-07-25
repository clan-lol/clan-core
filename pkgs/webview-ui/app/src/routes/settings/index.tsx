import { callApi } from "@/src/api";
import {
  SubmitHandler,
  createForm,
  required,
  setValue,
} from "@modular-forms/solid";
import {
  activeURI,
  setClanList,
  setActiveURI,
  setRoute,
  clanList,
} from "@/src/App";
import { createEffect, createSignal, For, Show } from "solid-js";
import { createQuery } from "@tanstack/solid-query";
import { useFloating } from "@/src/floating";
import {
  arrow,
  autoUpdate,
  flip,
  hide,
  offset,
  shift,
  size,
} from "@floating-ui/dom";

export const registerClan = async () => {
  try {
    const loc = await callApi("open_file", {
      file_request: { mode: "select_folder" },
    });
    console.log({ loc }, loc.status);
    if (loc.status === "success" && loc.data) {
      // @ts-expect-error: data is a string
      setClanList((s) => {
        const res = new Set([...s, loc.data]);
        return Array.from(res);
      });
      setActiveURI(loc.data);
      setRoute((r) => {
        if (r === "welcome") return "machines";
        return r;
      });
      return loc.data;
    }
  } catch (e) {
    //
  }
};

interface ClanDetailsProps {
  clan_dir: string;
}
const ClanDetails = (props: ClanDetailsProps) => {
  const { clan_dir } = props;

  const details = createQuery(() => ({
    queryKey: [clan_dir, "meta"],
    queryFn: async () => {
      const result = await callApi("show_clan_meta", { uri: clan_dir });
      if (result.status === "error") throw new Error("Failed to fetch data");
      return result.data;
    },
  }));

  const [reference, setReference] = createSignal<HTMLElement>();
  const [floating, setFloating] = createSignal<HTMLElement>();
  const [arrowEl, setArrowEl] = createSignal<HTMLElement>();

  // `position` is a reactive object.
  const position = useFloating(reference, floating, {
    placement: "top",

    // pass options. Ensure the cleanup function is returned.
    whileElementsMounted: (reference, floating, update) =>
      autoUpdate(reference, floating, update, {
        animationFrame: true,
      }),
    middleware: [
      offset(5),
      shift(),
      flip(),

      hide({
        strategy: "referenceHidden",
      }),
    ],
  });

  return (
    <div class="stat">
      <div class="stat-figure text-primary">
        <div class="join">
          <button
            class=" join-item btn-sm"
            classList={{
              "btn btn-ghost btn-outline": activeURI() !== clan_dir,
              "badge badge-primary": activeURI() === clan_dir,
            }}
            disabled={activeURI() === clan_dir}
            onClick={() => {
              setActiveURI(clan_dir);
            }}
          >
            {activeURI() === clan_dir ? "active" : "select"}
          </button>
          <button
            popovertarget={`clan-delete-popover-${clan_dir}`}
            popovertargetaction="toggle"
            ref={setReference}
            class="btn btn-ghost btn-outline join-item btn-sm"
          >
            Remove
          </button>
          <div
            popover="auto"
            id={`clan-delete-popover-${clan_dir}`}
            ref={setFloating}
            style={{
              position: position.strategy,
              top: `${position.y ?? 0}px`,
              left: `${position.x ?? 0}px`,
            }}
            class="bg-transparent"
          >
            <button
              class="btn btn-warning btn-sm"
              onClick={() => {
                setClanList((s) =>
                  s.filter((v, idx) => {
                    if (v == clan_dir) {
                      setActiveURI(
                        clanList()[idx - 1] || clanList()[idx + 1] || null
                      );
                      return false;
                    }
                    return true;
                  })
                );
              }}
            >
              Remove from App
            </button>
          </div>
        </div>
      </div>
      <div class="stat-title">Clan URI</div>

      <Show when={details.isSuccess}>
        <div
          class="stat-value"
          // classList={{
          //   "text-primary": activeURI() === clan_dir,
          // }}
        >
          {details.data?.name}
        </div>
      </Show>
      <Show
        when={details.isSuccess && details.data?.description}
        fallback={<div class="stat-desc text-lg">{clan_dir}</div>}
      >
        <div
          class="stat-desc text-lg"
          // classList={{
          //   "text-primary": activeURI() === clan_dir,
          // }}
        >
          {details.data?.description}
        </div>
      </Show>
    </div>
  );
};

export const Settings = () => {
  return (
    <div class="card card-normal">
      <div class="card-body">
        <div class="label">
          <div class="label-text">Registered Clans</div>
          <button
            class="btn btn-square btn-primary"
            onClick={() => {
              registerClan();
            }}
          >
            <span class="material-icons">add</span>
          </button>
        </div>
        <div class="stats stats-vertical shadow">
          <For each={clanList()}>
            {(value) => <ClanDetails clan_dir={value} />}
          </For>
        </div>
      </div>
    </div>
  );
};
