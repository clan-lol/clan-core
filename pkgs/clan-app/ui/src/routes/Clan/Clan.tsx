import { RouteSectionProps } from "@solidjs/router";
import { Component, JSX, Show, createSignal, onMount } from "solid-js";
import { useClanURI } from "@/src/hooks/clan";
import { CubeScene } from "@/src/scene/cubes";
import { MachinesQueryResult, useMachinesQuery } from "@/src/queries/queries";
import { callApi } from "@/src/hooks/api";
import { store, setStore } from "@/src/stores/clan";
import { produce } from "solid-js/store";
import { Button } from "@/src/components/Button/Button";
import { Splash } from "@/src/scene/splash";
import cx from "classnames";
import "./Clan.css";
import { Modal } from "@/src/components/Modal/Modal";
import { TextInput } from "@/src/components/Form/TextInput";
import { createForm, FieldValues, reset } from "@modular-forms/solid";

export const Clan: Component<RouteSectionProps> = (props) => {
  return (
    <>
      <div
        style={{
          position: "absolute",
          top: 0,
        }}
      >
        {props.children}
      </div>
      <ClanSceneController />
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
    <div ref={(el) => (container = el)} class="create-backdrop">
      <Modal
        mount={container!}
        onClose={() => {
          reset(form);
          props.onClose();
        }}
        class="create-modal"
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
                    input={{ ...props, placeholder: "name" }}
                  />
                </>
              )}
            </Field>

            <div class="flex w-full items-center justify-end gap-4">
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

const ClanSceneController = () => {
  const clanURI = useClanURI();

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

  return (
    <SceneDataProvider clanURI={clanURI}>
      {({ query }) => {
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
            <div
              class="flex flex-row"
              style={{ position: "absolute", top: "10px", left: "10px" }}
            >
              <Button
                ghost
                onClick={() => {
                  setStore(
                    produce((s) => {
                      for (const machineId in s.sceneData[clanURI]) {
                        // Reset the position of each machine to [0, 0]
                        s.sceneData[clanURI] = {};
                      }
                    }),
                  );
                }}
              >
                Reset Store
              </Button>
              <Button
                ghost
                onClick={() => {
                  console.log("Refetching API");
                  query.refetch();
                }}
              >
                Refetch API
              </Button>
            </div>
            {/* TODO: Add minimal display time */}
            <div
              class={cx({ "fade-out": !query.isLoading && loadingCooldown() })}
            >
              <Splash />
            </div>

            <CubeScene
              isLoading={query.isLoading}
              cubesQuery={query}
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
  children: (sceneData: { query: MachinesQueryResult }) => JSX.Element;
}) => {
  const machinesQuery = useMachinesQuery({ clanURI: props.clanURI });

  // This component can be used to provide scene data or context if needed
  return props.children({ query: machinesQuery });
};
