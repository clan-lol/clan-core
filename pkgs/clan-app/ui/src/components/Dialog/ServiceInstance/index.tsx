import {
  createStepper,
  getStepStore,
  StepperProvider,
  useStepper,
} from "@/src/hooks/stepper";
import {
  createEffect,
  Show,
  onMount,
  For,
  Component,
  onCleanup,
} from "solid-js";
import Icon from "@/src/components/Icon/Icon";
import { Combobox } from "@kobalte/core/combobox";
import { Typography } from "@/src/components/Typography/Typography";

import { createForm, FieldValues } from "@modular-forms/solid";
import styles from "./ServiceInstance.module.css";
import { TextInput } from "@/src/components/Form/TextInput";
import { Button } from "@/src/components/Button/Button";
import cx from "classnames";
import { BackButton } from "../../../workflows/Steps";
import { SearchMultiple } from "@/src/components/Search/MultipleSearch";
import { TagSelect } from "@/src/components/Search/TagSelect";
import { Tag } from "@/src/components/Tag/Tag";
import {
  ClanMember,
  useClanContext,
  useMachinesContext,
  useUIContext,
  ToolbarServiceInstanceMode,
  useServiceInstancesContext,
} from "@/src/models";
import { produce, unwrap } from "solid-js/store";

type Role = {
  id: string;
  settings: Record<string, unknown>;
  members: ClanMember[];
};
type ServiceStoreType = {
  roles: Role[];
  instanceName: string;
  currentRole: Role | null;
};

const ServiceInstanceWorkflow: Component = (props) => {
  const [ui] = useUIContext();
  const mode = ui.toolbarMode as ToolbarServiceInstanceMode;
  const stepper = createStepper(
    { steps },
    {
      initialStep: "view:members",
      initialStoreData:
        mode.subtype === "edit"
          ? {
              instanceName: mode.serviceInstance.data.name,
              roles: mode.serviceInstance.data.roles.sorted.map((role) => ({
                id: role.id,
                settings: unwrap(role.settings),
                members: role.members.slice(0),
              })),
              currentRole: null,
            }
          : {
              // Default to the module name, until we support multiple instances
              instanceName: mode.service.id,
              roles: mode.service.roles.sorted.map((role) => ({
                id: role.id,
                settings: {},
                members: [],
              })),
              currentRole: null,
            },
    },
  );

  return (
    <div class="absolute bottom-full left-1/2 mb-2 -translate-x-1/2">
      <StepperProvider stepper={stepper}>
        <div class="w-[30rem]">{stepper.currentStep().content()}</div>
      </StepperProvider>
    </div>
  );
};
export default ServiceInstanceWorkflow;

interface RolesForm extends FieldValues {
  instanceName: string;
}
const ConfigureServiceInstance = () => {
  const [ui, { setToolbarMode }] = useUIContext();
  const [, { addServiceInstance, updateServiceInstanceData }] =
    useServiceInstancesContext();
  const [clan] = useClanContext();
  const stepper = useStepper<ServiceSteps>();

  const [store, setStore] = getStepStore<ServiceStoreType>(stepper);
  const [formStore, { Form, Field }] = createForm<RolesForm>({
    initialValues: {
      instanceName: store.instanceName,
    },
  });

  const onSubmit = async (values: RolesForm) => {
    const mode = ui.toolbarMode as ToolbarServiceInstanceMode;
    const data = {
      name: values.instanceName,
      roles: Object.fromEntries(
        store.roles.map((role) => [
          role.id,
          {
            settings: {},
            machines: role.members
              .filter(({ type }) => type === "machine")
              .map(({ name }) => name),
            tags: role.members
              .filter(({ type }) => type === "tag")
              .map(({ name }) => name),
          },
        ]),
      ),
    };
    if (mode.subtype === "create") {
      await addServiceInstance(data, mode.service);
    } else {
      await updateServiceInstanceData(data);
    }
    setToolbarMode({ type: "select" });
  };

  return (
    <Form onSubmit={onSubmit}>
      <div class={cx(styles.header, styles.backgroundAlt)}>
        <div class="overflow-hidden rounded-sm">
          <Icon icon="Services" size={36} inverted />
        </div>
        <div class="flex flex-col">
          <Typography hierarchy="body" size="s" weight="medium" inverted>
            {store.instanceName}
          </Typography>
          <Field name="instanceName">
            {(field, input) => (
              <TextInput
                {...field}
                value={field.value}
                size="s"
                inverted
                required
                readOnly={true}
                orientation="horizontal"
                input={input}
              />
            )}
          </Field>
        </div>
        <Button
          icon="Close"
          ghost
          size="s"
          in="ConfigureService"
          onClick={() => setToolbarMode({ type: "select" })}
        />
      </div>
      <div class={styles.content}>
        <For each={store.roles}>
          {(role) => {
            return (
              <TagSelect<ClanMember>
                label={role.id}
                renderItem={(member) => (
                  <Tag
                    inverted
                    icon={(tag) => (
                      <Icon
                        icon={member.type === "machine" ? "Machine" : "Tag"}
                        size="0.5rem"
                        inverted={tag.inverted}
                      />
                    )}
                  >
                    {member.name}
                  </Tag>
                )}
                values={role.members}
                options={clan().members}
                onClick={() => {
                  setStore("currentRole", role);
                  stepper.next();
                }}
              />
            );
          }}
        </For>
      </div>
      <div class={cx(styles.footer, styles.backgroundAlt)}>
        <Button hierarchy="secondary" type="submit">
          <Show
            when={
              (ui.toolbarMode as ToolbarServiceInstanceMode).subtype ===
              "create"
            }
            fallback={"Save Changes"}
          >
            Add Service
          </Show>
        </Button>
      </div>
    </Form>
  );
};

export type TagType =
  | {
      value: string;
      label: string;
      type: "machine";
    }
  | {
      value: string;
      label: string;
      type: "tag";
      members: string[];
    };

const ConfigureRole = () => {
  const [ui, { setToolbarMode }] = useUIContext();
  const [clan] = useClanContext();
  const [, { setHighlightedMachines, machinesByTag }] = useMachinesContext();
  const stepper = useStepper<ServiceSteps>();
  const [store, setStore] = getStepStore<ServiceStoreType>(stepper);
  const role = store.currentRole!;

  onMount(() => {
    setToolbarMode({
      ...(ui.toolbarMode as ToolbarServiceInstanceMode),
      highlighting: true,
    });
    createEffect(() => {
      const highlighted = role.members
        .filter(({ type }) => type === "machine")
        .map(({ name }) => name);
      setHighlightedMachines(highlighted);
    });
  });

  onCleanup(() => {
    setToolbarMode({
      ...(ui.toolbarMode as ToolbarServiceInstanceMode),
      highlighting: false,
    });
  });

  return (
    <form onSubmit={() => stepper.setActiveStep("view:members")}>
      <div class={cx(styles.backgroundAlt, "rounded-md")}>
        <div class="flex w-full flex-col ">
          <SearchMultiple<ClanMember>
            values={role.members}
            options={clan().members}
            headerClass={cx(styles.backgroundAlt, "flex flex-col gap-2.5")}
            headerChildren={
              <div class="flex w-full gap-2.5">
                <BackButton ghost size="xs" hierarchy="primary" />
                <Typography
                  hierarchy="body"
                  size="s"
                  weight="medium"
                  inverted
                  transform="capitalize"
                >
                  Select {role.id}
                </Typography>
              </div>
            }
            placeholder={"Search for Machine or Tags"}
            renderItem={(item, opts) => (
              <div class={cx("flex w-full items-center gap-2 px-3 py-2")}>
                <Combobox.ItemIndicator>
                  <Show when={opts.selected} fallback={<Icon icon="Code" />}>
                    <Icon icon="Checkmark" color="primary" inverted />
                  </Show>
                </Combobox.ItemIndicator>
                <Combobox.ItemLabel class="flex items-center gap-2">
                  <Typography
                    hierarchy="body"
                    size="s"
                    weight="medium"
                    inverted
                  >
                    {item.name}
                  </Typography>
                  <Show when={item.type === "tag" && item}>
                    {(tag) => (
                      <Typography
                        hierarchy="body"
                        size="xs"
                        weight="medium"
                        inverted
                        color="secondary"
                        tag="div"
                      >
                        {machinesByTag(tag().name).length}
                      </Typography>
                    )}
                  </Show>
                </Combobox.ItemLabel>
                <Icon
                  icon={item.type === "machine" ? "Machine" : "Tag"}
                  color="quaternary"
                  inverted
                  in="ConfigureRole"
                />
              </div>
            )}
            height="20rem"
            virtualizerOptions={{
              estimateSize: () => 38,
            }}
            onChange={(members) => {
              setStore(
                "currentRole",
                produce((role) => (role!.members = members)),
              );
            }}
          />
        </div>
        <div class={cx(styles.footer, styles.backgroundAlt)}>
          <Button hierarchy="secondary" type="submit">
            Confirm
          </Button>
        </div>
      </div>
    </form>
  );
};

const steps = [
  {
    id: "view:members",
    content: ConfigureServiceInstance,
  },
  {
    id: "select:members",
    content: ConfigureRole,
  },
  { id: "settings", content: () => <div>Adjust settings here.</div> },
] as const;

type ServiceSteps = typeof steps;
