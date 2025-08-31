import { RouteSectionProps, useNavigate } from "@solidjs/router";
import {
  Component,
  createContext,
  createEffect,
  createMemo,
  createSignal,
  on,
  onMount,
  Show,
  Signal,
  useContext,
} from "solid-js";
import {
  buildClanPath,
  buildMachinePath,
  maybeUseMachineName,
  useClanURI,
  useMachineName,
} from "@/src/hooks/clan";
import { CubeScene, setWorldMode, worldMode } from "@/src/scene/cubes";
import {
  ClanDetails,
  MachinesQueryResult,
  useClanDetailsQuery,
  useClanListQuery,
  useMachinesQuery,
} from "@/src/hooks/queries";
import { clanURIs, setStore, store } from "@/src/stores/clan";
import { produce } from "solid-js/store";
import { Splash } from "@/src/scene/splash";
import cx from "classnames";
import styles from "./Clan.module.css";
import { Sidebar } from "@/src/components/Sidebar/Sidebar";
import { UseQueryResult } from "@tanstack/solid-query";
import { ListClansModal } from "@/src/modals/ListClansModal/ListClansModal";
import {
  ServiceWorkflow,
  SubmitServiceHandler,
} from "@/src/workflows/Service/Service";
import { useApiClient } from "@/src/hooks/ApiClient";
import toast from "solid-toast";
import { AddMachine } from "@/src/workflows/AddMachine/AddMachine";

interface ClanContextProps {
  clanURI: string;
  machinesQuery: MachinesQueryResult;
  activeClanQuery: UseQueryResult<ClanDetails>;
  otherClanQueries: UseQueryResult<ClanDetails>[];
  allClansQueries: UseQueryResult<ClanDetails>[];

  isLoading(): boolean;
  isError(): boolean;

  showAddMachine(): boolean;
  setShowAddMachine(value: boolean): void;
}

class DefaultClanContext implements ClanContextProps {
  public readonly clanURI: string;

  public readonly activeClanQuery: UseQueryResult<ClanDetails>;
  public readonly otherClanQueries: UseQueryResult<ClanDetails>[];
  public readonly allClansQueries: UseQueryResult<ClanDetails>[];

  public readonly machinesQuery: MachinesQueryResult;

  allQueries: UseQueryResult[];

  showAddMachineSignal: Signal<boolean>;

  constructor(
    clanURI: string,
    machinesQuery: MachinesQueryResult,
    activeClanQuery: UseQueryResult<ClanDetails>,
    otherClanQueries: UseQueryResult<ClanDetails>[],
  ) {
    this.clanURI = clanURI;
    this.machinesQuery = machinesQuery;

    this.activeClanQuery = activeClanQuery;
    this.otherClanQueries = otherClanQueries;
    this.allClansQueries = [activeClanQuery, ...otherClanQueries];

    this.allQueries = [machinesQuery, activeClanQuery, ...otherClanQueries];

    this.showAddMachineSignal = createSignal(false);
  }

  isLoading(): boolean {
    return this.allQueries.some((q) => q.isLoading);
  }

  isError(): boolean {
    return this.activeClanQuery.isError;
  }

  setShowAddMachine(value: boolean) {
    const [_, setShow] = this.showAddMachineSignal;
    setShow(value);
  }

  showAddMachine(): boolean {
    const [show, _] = this.showAddMachineSignal;
    return show();
  }
}

export const ClanContext = createContext<ClanContextProps>();

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

  return (
    <ClanContext.Provider
      value={
        new DefaultClanContext(
          clanURI,
          machinesQuery,
          activeClanQuery,
          otherClanQueries,
        )
      }
    >
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
  const ctx = useContext(ClanContext);
  if (!ctx) {
    throw new Error("ClanContext not found");
  }

  const navigate = useNavigate();

  const [showService, setShowService] = createSignal(false);

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

  const client = useApiClient();
  const handleSubmitService: SubmitServiceHandler = async (
    instance,
    action,
  ) => {
    console.log(action, "Instance", instance);

    if (action !== "create") {
      toast.error("Only creating new services is supported");
      return;
    }
    const call = client.fetch("create_service_instance", {
      flake: {
        identifier: ctx.clanURI,
      },
      module_ref: instance.module,
      roles: instance.roles,
    });
    const result = await call.result;

    if (result.status === "error") {
      toast.error("Error creating service instance");
      console.error("Error creating service instance", result.errors);
    }
    toast.success("Created");
    setShowService(false);
    setWorldMode("select");
  };

  createEffect(
    on(worldMode, (mode) => {
      if (mode === "service") {
        setShowService(true);
      } else {
        // TODO: request soft close instead of forced close
        setShowService(false);
      }
    }),
  );

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
          <Show when={showService()}>
            <ServiceWorkflow
              handleSubmit={handleSubmitService}
              onClose={() => {
                setShowService(false);
                setWorldMode("select");
                currentPromise()?.resolve({ id: "0" });
              }}
            />
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
