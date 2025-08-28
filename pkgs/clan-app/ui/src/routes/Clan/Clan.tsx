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
  useContext,
} from "solid-js";
import {
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
import { callApi } from "@/src/hooks/api";
import { clanURIs, setStore, store } from "@/src/stores/clan";
import { produce } from "solid-js/store";
import { Button } from "@/src/components/Button/Button";
import { Splash } from "@/src/scene/splash";
import cx from "classnames";
import styles from "./Clan.module.css";
import { Modal } from "@/src/components/Modal/Modal";
import { TextInput } from "@/src/components/Form/TextInput";
import { createForm, FieldValues, reset } from "@modular-forms/solid";
import { Sidebar } from "@/src/components/Sidebar/Sidebar";
import { UseQueryResult } from "@tanstack/solid-query";
import { ListClansModal } from "@/src/modals/ListClansModal/ListClansModal";
import {
  ServiceWorkflow,
  SubmitServiceHandler,
} from "@/src/workflows/Service/Service";
import { useApiClient } from "@/src/hooks/ApiClient";
import toast from "solid-toast";

interface ClanContextProps {
  clanURI: string;
  machinesQuery: MachinesQueryResult;
  activeClanQuery: UseQueryResult<ClanDetails>;
  otherClanQueries: UseQueryResult<ClanDetails>[];
  allClansQueries: UseQueryResult<ClanDetails>[];

  isLoading(): boolean;
  isError(): boolean;
}

class DefaultClanContext implements ClanContextProps {
  public readonly clanURI: string;

  public readonly activeClanQuery: UseQueryResult<ClanDetails>;
  public readonly otherClanQueries: UseQueryResult<ClanDetails>[];
  public readonly allClansQueries: UseQueryResult<ClanDetails>[];

  public readonly machinesQuery: MachinesQueryResult;

  allQueries: UseQueryResult[];

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
  }

  isLoading(): boolean {
    return this.allQueries.some((q) => q.isLoading);
  }

  isError(): boolean {
    return this.activeClanQuery.isError;
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

interface CreateFormValues extends FieldValues {
  name: string;
}

interface MockProps {
  onClose: () => void;
  onSubmit: (formValues: CreateFormValues) => void;
}

const MockCreateMachine = (props: MockProps) => {
  const [form, { Form, Field, FieldArray }] = createForm<CreateFormValues>();

  return (
    <Modal
      open={true}
      onClose={() => {
        reset(form);
        props.onClose();
      }}
      class={cx(styles.createModal)}
      title="Create Machine"
    >
      <Form class="flex flex-col" onSubmit={props.onSubmit}>
        <Field name="name">
          {(field, props) => (
            <>
              <TextInput
                {...field}
                label="Name"
                size="s"
                required={true}
                input={{ ...props, placeholder: "name", autofocus: true }}
              />
            </>
          )}
        </Field>

        <div class="mt-4 flex w-full items-center justify-end gap-4">
          <Button size="s" hierarchy="secondary" onClick={props.onClose}>
            Cancel
          </Button>
          <Button size="s" type="submit" hierarchy="primary" onClick={close}>
            Create
          </Button>
        </div>
      </Form>
    </Modal>
  );
};

const ClanSceneController = (props: RouteSectionProps) => {
  const ctx = useContext(ClanContext);
  if (!ctx) {
    throw new Error("ClanContext not found");
  }

  const navigate = useNavigate();

  const [showService, setShowService] = createSignal(false);

  const [showModal, setShowModal] = createSignal(false);
  const [currentPromise, setCurrentPromise] = createSignal<{
    resolve: ({ id }: { id: string }) => void;
    reject: (err: unknown) => void;
  } | null>(null);

  const onCreate = async (): Promise<{ id: string }> => {
    return new Promise((resolve, reject) => {
      setShowModal(true);
      setCurrentPromise({ resolve, reject });
    });
  };

  const onAddService = async (): Promise<{ id: string }> => {
    return new Promise((resolve, reject) => {
      setShowService((v) => !v);
      console.log("setting current promise");
      setCurrentPromise({ resolve, reject });
    });
  };

  const sendCreate = async (values: CreateFormValues) => {
    const api = callApi("create_machine", {
      opts: {
        clan_dir: {
          identifier: ctx.clanURI,
        },
        machine: {
          name: values.name,
        },
      },
    });
    const res = await api.result;
    if (res.status === "error") {
      // TODO: Handle displaying errors
      console.error("Error creating machine:");

      // Important: rejects the promise
      throw new Error(res.errors[0].message);
    }

    // trigger a refetch of the machines query
    ctx.machinesQuery.refetch();

    return { id: values.name };
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
    //
    currentPromise()?.resolve({ id: "0" });
    setShowService(false);
  };

  createEffect(
    on(worldMode, (mode) => {
      if (mode === "service") {
        setShowService(true);
      } else {
        // todo: request close instead of force close
        setShowService(false);
      }
    }),
  );

  return (
    <>
      <Show when={loadingError()}>
        <ListClansModal error={loadingError()} />
      </Show>
      <Show when={showModal()}>
        <MockCreateMachine
          onClose={() => {
            setShowModal(false);
            currentPromise()?.reject(new Error("User cancelled"));
          }}
          onSubmit={async (values) => {
            try {
              const result = await sendCreate(values);
              currentPromise()?.resolve(result);
              setShowModal(false);
            } catch (err) {
              currentPromise()?.reject(err);
              setShowModal(false);
            }
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
                setWorldMode("default");
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
