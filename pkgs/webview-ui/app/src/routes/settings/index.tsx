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
import { For } from "solid-js";

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
            {(value) => (
              <div class="stat">
                <div class="stat-figure text-primary">
                  <div class="join">
                    <button
                      class=" join-item btn-sm"
                      classList={{
                        "btn btn-ghost btn-outline": activeURI() !== value,
                        "badge badge-primary": activeURI() === value,
                      }}
                      disabled={activeURI() === value}
                      onClick={() => {
                        setActiveURI(value);
                      }}
                    >
                      {activeURI() === value ? "active" : "select"}
                    </button>
                    <button
                      class="btn btn-ghost btn-outline join-item btn-sm"
                      onClick={() => {
                        setClanList((s) =>
                          s.filter((v, idx) => {
                            if (v == value) {
                              setActiveURI(
                                clanList()[idx - 1] ||
                                  clanList()[idx + 1] ||
                                  null
                              );
                              return false;
                            }
                            return true;
                          })
                        );
                        // if (activeURI() === value) {
                        //   setActiveURI();
                        // }
                      }}
                    >
                      Remove URI
                    </button>
                  </div>
                </div>
                <div class="stat-title">Clan URI</div>

                <div
                  class="stat-desc text-lg"
                  classList={{
                    "text-primary": activeURI() === value,
                  }}
                >
                  {value}
                </div>
              </div>
            )}
          </For>
        </div>
      </div>
    </div>
  );
};
