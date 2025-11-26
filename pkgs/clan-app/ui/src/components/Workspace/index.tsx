import { RouteSectionProps, useLocation, useNavigate } from "@solidjs/router";
import {
  Component,
  createContext,
  createEffect,
  createMemo,
  createSignal,
  ErrorBoundary,
  on,
  onMount,
  Show,
  Suspense,
  useContext,
} from "solid-js";
import {
  buildClanPath,
  buildMachinePath,
  maybeUseMachineName,
  useClanURI,
  useMachineName,
} from "@/src/hooks/clan";
import { CubeScene } from "@/src/scene/cubes";
import {
  ClanDetails,
  ListServiceInstances,
  MachinesQueryResult,
  useClanDetailsQuery,
  useClanListQuery,
  useMachinesQuery,
  useServiceInstancesQuery,
} from "@/src/hooks/queries";
import { clanURIs, setStore, store } from "@/src/stores/clan";
import { produce } from "solid-js/store";
import cx from "classnames";
import styles from "./Workspace.module.css";
import { Sidebar } from "@/src/components/Sidebar/Sidebar";
import { UseQueryResult } from "@tanstack/solid-query";
import { ListClansModal } from "@/src/modals/ListClansModal/ListClansModal";

import { AddMachine } from "@/src/workflows/AddMachine/AddMachine";
import { SelectService } from "@/src/workflows/Service/SelectServiceFlyout";
import { useClanContext } from "@/src/contexts/ClanContext";
import { Service } from "../../routes/Service/Service";
import SidebarMachine from "../Sidebar/SidebarMachine";

export default function Clan() {
  const { clans } = useClanContext()!;
  const activeMachine = () => clans()?.active?.machines()?.active;

  return (
    <>
      <div
        class={cx(styles.sidebarContainer, {
          [styles.machineSelected]: activeMachine(),
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
      <Show when={activeMachine()}>
        <SidebarMachine machine={activeMachine()!} />
      </Show>
    </>
  );
}
