import { RouteSectionProps, useLocation, useNavigate } from "@solidjs/router";
import {
  Component,
  createContext,
  createEffect,
  createMemo,
  createSignal,
  on,
  onMount,
  Show,
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
import { Splash } from "@/src/scene/splash";
import cx from "classnames";
import styles from "./Clan.module.css";
import { Sidebar } from "@/src/components/Sidebar/Sidebar";
import { UseQueryResult } from "@tanstack/solid-query";
import { ListClansModal } from "@/src/modals/ListClansModal/ListClansModal";

import { AddMachine } from "@/src/workflows/AddMachine/AddMachine";
import { SelectService } from "@/src/workflows/Service/SelectServiceFlyout";

export type WorldMode = "default" | "select" | "service" | "create" | "move";

function createClanContext(
  clanURI: string,
  machinesQuery: MachinesQueryResult,
  activeClanQuery: UseQueryResult<ClanDetails>,
  otherClanQueries: UseQueryResult<ClanDetails>[],
  serviceInstancesQuery: UseQueryResult<ListServiceInstances>,
) {
  const [worldMode, setWorldMode] = createSignal<WorldMode>("select");
  const [showAddMachine, setShowAddMachine] = createSignal(false);

  const navigate = useNavigate();
  const location = useLocation();

  const allClansQueries = [activeClanQuery, ...otherClanQueries];
  const allQueries = [machinesQuery, ...allClansQueries, serviceInstancesQuery];

  return {
    clanURI,
    machinesQuery,
    activeClanQuery,
    otherClanQueries,
    allClansQueries,
    serviceInstancesQuery,
    isLoading: () => allQueries.some((q) => q.isLoading),
    isError: () => activeClanQuery.isError,
    showAddMachine,
    setShowAddMachine,
    navigateToRoot: () => {
      if (location.pathname === buildClanPath(clanURI)) return;
      navigate(buildClanPath(clanURI), { replace: true });
    },
    setWorldMode,
    worldMode,
  };
}

const ClanContext = createContext<
  ReturnType<typeof createClanContext> | undefined
>();

export const useClanContext = () => {
  const ctx = useContext(ClanContext);
  if (!ctx) {
    throw new Error("ClanContext not found");
  }
  return ctx;
};

export const Clan: Component<RouteSectionProps> = (props) => {
  const clanURI = useClanURI();
  const activeClanQuery = useClanDetailsQuery(clanURI);

  createEffect(() => {
    if (activeClanQuery.isError) {
      console.error("Error loading active clan", activeClanQuery.error);
    }
  });

  const otherClanQueries = useClanListQuery(
    clanURIs().filter((uri) => uri != clanURI),
    clanURI,
  );

  const machinesQuery = useMachinesQuery(clanURI);
  const serviceInstancesQuery = useServiceInstancesQuery(clanURI);

  const ctx = createClanContext(
    clanURI,
    machinesQuery,
    activeClanQuery,
    otherClanQueries,
    serviceInstancesQuery,
  );

  return (
    <ClanContext.Provider value={ctx}>
      <div
        class={cx(styles.sidebarContainer, {
          [styles.machineSelected]: useMachineName(),
        })}
      >
        <Sidebar />
      </div>
      {props.children}
      <ClanSceneController {...props} />
    </ClanContext.Provider>
  );
};

const ClanSceneController = (props: RouteSectionProps) => {
  const ctx = useClanContext();

  const navigate = useNavigate();

  const [currentPromise, setCurrentPromise] = createSignal<{
    resolve: ({ id }: { id: string }) => void;
    reject: (err: unknown) => void;
  } | null>(null);

  const onCreate = async (): Promise<{ id: string }> => {
    return new Promise((resolve, reject) => {
      ctx.setShowAddMachine(true);
      setCurrentPromise({ resolve, reject });
    });
  };

  const [loadingError, setLoadingError] = createSignal<
    { title: string; description: string } | undefined
  >();
  const [loadingCooldown, setLoadingCooldown] = createSignal(false);

  onMount(() => {
    setTimeout(() => {
      setLoadingCooldown(true);
    }, 1500);
  });

  createEffect(() => {
    if (ctx.activeClanQuery.isError) {
      setLoadingError({
        title: "Error loading clan",
        description: ctx.activeClanQuery.error.message,
      });
    }
  });

  const [selectedIds, setSelectedIds] = createSignal<Set<string>>(new Set());

  const onMachineSelect = (ids: Set<string>) => {
    // Get the first selected ID and navigate to its machine details
    const selected = ids.values().next().value;
    if (selected) {
      navigate(buildMachinePath(ctx.clanURI, selected));
    } else {
      navigate(buildClanPath(ctx.clanURI));
    }
  };

  const machine = createMemo(() => maybeUseMachineName());

  createEffect(
    on(machine, (machineId) => {
      if (machineId) {
        setSelectedIds(() => {
          const res = new Set<string>();
          res.add(machineId);
          return res;
        });
      } else {
        setSelectedIds(new Set<string>());
      }
    }),
  );

  const location = useLocation();

  return (
    <>
      <Show when={loadingError()}>
        <ListClansModal error={loadingError()} />
      </Show>
      <Show when={ctx.showAddMachine()}>
        <AddMachine
          onCreated={async (id) => {
            const promise = currentPromise();
            if (promise) {
              await ctx.machinesQuery.refetch();
              promise.resolve({ id });
              setCurrentPromise(null);
            }
          }}
          onClose={() => {
            ctx.setShowAddMachine(false);
          }}
        />
      </Show>
      <div
        class={cx({
          [styles.fadeOut]: !ctx.isLoading() && loadingCooldown(),
        })}
      >
        <Splash />
      </div>

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
        setMachinePos={(machineId: string, pos: [number, number] | null) => {
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
    </>
  );
};
