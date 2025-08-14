import { RouteSectionProps } from "@solidjs/router";
import {
  Component,
  JSX,
  Show,
  createEffect,
  createMemo,
  createSignal,
  on,
  onMount,
} from "solid-js";
import {
  buildMachinePath,
  maybeUseMachineName,
  useClanURI,
} from "@/src/hooks/clan";
import { CubeScene } from "@/src/scene/cubes";
import {
  ClanListQueryResult,
  MachinesQueryResult,
  useClanListQuery,
  useMachinesQuery,
} from "@/src/hooks/queries";
import { callApi } from "@/src/hooks/api";
import { store, setStore, clanURIs, setActiveClanURI } from "@/src/stores/clan";
import { produce } from "solid-js/store";
import { Button } from "@/src/components/Button/Button";
import { Splash } from "@/src/scene/splash";
import cx from "classnames";
import styles from "./Clan.module.css";
import { Modal } from "@/src/components/Modal/Modal";
import { TextInput } from "@/src/components/Form/TextInput";
import { createForm, FieldValues, reset } from "@modular-forms/solid";
import { Sidebar } from "@/src/components/Sidebar/Sidebar";
import { useNavigate } from "@solidjs/router";

export const Clan: Component<RouteSectionProps> = (props) => {
  return (
    <>
      <Sidebar class={cx(styles.sidebar)} />
      {props.children}
      <ClanSceneController {...props} />
    </>
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
  let container: Node;

  const [form, { Form, Field, FieldArray }] = createForm<CreateFormValues>();

  return (
    <div ref={(el) => (container = el)} class={cx(styles.createBackdrop)}>
      <Modal
        open={true}
        mount={container!}
        onClose={() => {
          reset(form);
          props.onClose();
        }}
        class={cx(styles.createModal)}
        title="Create Machine"
      >
        {() => (
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
              <Button
                size="s"
                type="submit"
                hierarchy="primary"
                onClick={close}
              >
                Create
              </Button>
            </div>
          </Form>
        )}
      </Modal>
    </div>
  );
};

const ClanSceneController = (props: RouteSectionProps) => {
  const clanURI = useClanURI();
  const navigate = useNavigate();

  const [dialogHandlers, setDialogHandlers] = createSignal<{
    resolve: ({ id }: { id: string }) => void;
    reject: (err: unknown) => void;
  } | null>(null);

  const onCreate = async (): Promise<{ id: string }> => {
    return new Promise((resolve, reject) => {
      setShowModal(true);
      setDialogHandlers({ resolve, reject });
    });
  };

  const sendCreate = async (values: CreateFormValues) => {
    const api = callApi("create_machine", {
      opts: {
        clan_dir: {
          identifier: clanURI,
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
    return { id: values.name };
  };

  const [showModal, setShowModal] = createSignal(false);

  const [loadingCooldown, setLoadingCooldown] = createSignal(false);
  onMount(() => {
    setTimeout(() => {
      setLoadingCooldown(true);
    }, 1500);
  });

  const [selectedIds, setSelectedIds] = createSignal<Set<string>>(new Set());

  const onMachineSelect = (ids: Set<string>) => {
    // Get the first selected ID and navigate to its machine details
    const selected = ids.values().next().value;
    if (selected) {
      navigate(buildMachinePath(clanURI, selected));
    }
  };

  const machine = createMemo(() => maybeUseMachineName());

  createEffect(() => {
    console.log("Selected clan:", clanURI);
  });

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

  return (
    <SceneDataProvider clanURI={clanURI}>
      {({ clansQuery, machinesQuery }) => {
        // a combination of the individual clan details query status and the machines query status
        // the cube scene needs the machines query, the sidebar needs the clans query and machines query results
        // so we wait on both before removing the loader to avoid any loading artefacts
        const isLoading = (): boolean => {
          // check the machines query first
          if (machinesQuery.isLoading) {
            return true;
          }

          // otherwise iterate the clans query and return early if we find a queries that is still loading
          for (const query of clansQuery) {
            if (query.isLoading) {
              return true;
            }
          }

          return false;
        };

        return (
          <>
            <Show when={showModal()}>
              <MockCreateMachine
                onClose={() => {
                  setShowModal(false);
                  dialogHandlers()?.reject(new Error("User cancelled"));
                }}
                onSubmit={async (values) => {
                  try {
                    const result = await sendCreate(values);
                    dialogHandlers()?.resolve(result);
                    setShowModal(false);
                  } catch (err) {
                    dialogHandlers()?.reject(err);
                    setShowModal(false);
                  }
                }}
              />
            </Show>
            <Button
              onClick={() => setActiveClanURI(undefined)}
              hierarchy="primary"
              class="absolute bottom-4 right-4"
            >
              close this clan
            </Button>
            <div
              class={cx({
                [styles.fadeOut]: !machinesQuery.isLoading && loadingCooldown(),
              })}
            >
              <Splash />
            </div>

            <CubeScene
              selectedIds={selectedIds}
              onSelect={onMachineSelect}
              isLoading={isLoading()}
              cubesQuery={machinesQuery}
              onCreate={onCreate}
              sceneStore={() => {
                const clanURI = useClanURI();
                return store.sceneData?.[clanURI];
              }}
              setMachinePos={(machineId: string, pos: [number, number]) => {
                console.log("calling setStore", machineId, pos);
                setStore(
                  produce((s) => {
                    if (!s.sceneData) {
                      s.sceneData = {};
                    }
                    if (!s.sceneData[clanURI]) {
                      s.sceneData[clanURI] = {};
                    }
                    if (!s.sceneData[clanURI][machineId]) {
                      s.sceneData[clanURI][machineId] = { position: pos };
                    } else {
                      s.sceneData[clanURI][machineId].position = pos;
                    }
                  }),
                );
              }}
            />
          </>
        );
      }}
    </SceneDataProvider>
  );
};

const SceneDataProvider = (props: {
  clanURI: string;
  children: (sceneData: {
    clansQuery: ClanListQueryResult;
    machinesQuery: MachinesQueryResult;
  }) => JSX.Element;
}) => {
  const clansQuery = useClanListQuery(clanURIs());
  const machinesQuery = useMachinesQuery(props.clanURI);

  // This component can be used to provide scene data or context if needed
  return props.children({ clansQuery, machinesQuery });
};
