import { Show } from "solid-js";
import { CubeScene } from "@/src/scene/cubes";
import cx from "classnames";
import styles from "./Workspace.module.css";
import Sidebar from "@/src/components/Sidebar";
import SidebarMachine from "../Sidebar/SidebarMachine";
import { useClanContext } from "../Context/ClanContext";
import { MachineContextProvider } from "../Context/MachineContext";

export default function Workspace() {
  const clan = useClanContext()!;

  return (
    <>
      <div
        class={cx(styles.sidebarContainer, {
          // [styles.machineSelected]: clan().machines()?.active,
        })}
      >
        <Sidebar />

        {/* <ErrorBoundary fallback={<p>Could not fetch clan data.</p>}>
        <Suspense fallback={<Splash />}>
          <CubeScene
            selectedIds={selectedIds}
            onSelect={onMachineSelect}
            isLoading={ctx.isLoading()}
            cubesQuery={ctx.machinesQuery}
            toolbarPopup={
              <Show when={ctx.worldMode() === "service"}>
                <Show
                  when={location.pathname.includes("/services/")}
                  fallback={
                    <SelectService
                      onClose={() => {
                        ctx.setWorldMode("select");
                      }}
                    />
                  }
                >
                  {props.children}
                </Show>
              </Show>
            }
            onCreate={onCreate}
            clanURI={ctx.clanURI}
            sceneStore={() => store.sceneData?.[ctx.clanURI]}
            setMachinePos={(
              machineId: string,
              pos: [number, number] | null,
            ) => {
              console.log("calling setStore", machineId, pos);
              setStore(
                produce((s) => {
                  if (!s.sceneData) s.sceneData = {};

                  if (!s.sceneData[ctx.clanURI]) s.sceneData[ctx.clanURI] = {};

                  if (pos === null) {
                    // Remove the machine entry if pos is null
                    Reflect.deleteProperty(s.sceneData[ctx.clanURI], machineId);

                    if (Object.keys(s.sceneData[ctx.clanURI]).length === 0) {
                      Reflect.deleteProperty(s.sceneData, ctx.clanURI);
                    }
                  } else {
                    // Set or update the machine position
                    s.sceneData[ctx.clanURI][machineId] = { position: pos };
                  }
                }),
              );
            }}
          />
        </Suspense>
      </ErrorBoundary> */}
      </div>
      {/* <Show when={clan().machines()?.active}>
        <MachineContextProvider machine={() => clan().machines()!.active!}>
          <SidebarMachine />
        </MachineContextProvider>
      </Show> */}
    </>
  );
}
