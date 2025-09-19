import {
  createStepper,
  getStepStore,
  StepperProvider,
  useStepper,
} from "@/src/hooks/stepper";
import { useClanURI, useServiceParams } from "@/src/hooks/clan";
import {
  MachinesQuery,
  TagsQuery,
  useMachinesQuery,
  useServiceInstances,
  useServiceModules,
  useTags,
} from "@/src/hooks/queries";
import {
  createEffect,
  createMemo,
  createSignal,
  Show,
  on,
  onMount,
  For,
} from "solid-js";
import Icon from "@/src/components/Icon/Icon";
import { Combobox } from "@kobalte/core/combobox";
import { Typography } from "@/src/components/Typography/Typography";

import { createForm, FieldValues } from "@modular-forms/solid";
import styles from "./Service.module.css";
import { TextInput } from "@/src/components/Form/TextInput";
import { Button } from "@/src/components/Button/Button";
import cx from "classnames";
import { BackButton } from "../Steps";
import { SearchMultiple } from "@/src/components/Search/MultipleSearch";
import { useMachineClick } from "@/src/scene/cubes";
import {
  clearAllHighlights,
  setHighlightGroups,
} from "@/src/scene/highlightStore";
import {
  getRoleMembers,
  RoleType,
  ServiceStoreType,
  SubmitServiceHandler,
} from "./models";
import { TagSelect } from "@/src/components/Search/TagSelect";
import { Tag } from "@/src/components/Tag/Tag";

const useOptions = (tagsQuery: TagsQuery, machinesQuery: MachinesQuery) =>
  createMemo<TagType[]>(() => {
    const tags = tagsQuery.data;
    const machines = machinesQuery.data;
    if (!tags || !machines) {
      return [];
    }

    const machineOptions = Object.keys(machines).map((m) => ({
      label: m,
      value: "m_" + m,
      type: "machine" as const,
    }));

    const tagOptions = [...tags.options, ...tags.special].map((tag) => ({
      type: "tag" as const,
      label: tag,
      value: "t_" + tag,
      members: Object.entries(machines)
        .filter(([_, v]) => v.data.tags?.includes(tag))
        .map(([k]) => k),
    }));

    return [...machineOptions, ...tagOptions].sort((a, b) =>
      a.label.localeCompare(b.label),
    );
  });

const sanitizeModuleInput = (
  input: string | undefined,
  core_input_name: string,
) => {
  if (!input) return null;

  if (input === core_input_name) return null;

  return input;
};

interface RolesForm extends FieldValues {
  roles: Record<string, string[]>;
  instanceName: string;
}
const ConfigureService = () => {
  const stepper = useStepper<ServiceSteps>();
  const clanURI = useClanURI();
  const machinesQuery = useMachinesQuery(clanURI);
  const serviceModulesQuery = useServiceModules(clanURI);
  const serviceInstancesQuery = useServiceInstances(clanURI);
  const routerProps = useServiceParams();

  const [store, set] = getStepStore<ServiceStoreType>(stepper);

  const [formStore, { Form, Field }] = createForm<RolesForm>({
    initialValues: {
      // Default to the module name, until we support multiple instances
      instanceName: routerProps.id,
    },
  });

  const selectedModule = createMemo(() => {
    if (!serviceModulesQuery.data) return undefined;
    return serviceModulesQuery.data.modules.find(
      (m) =>
        m.usage_ref.name === routerProps.name &&
        // left side is string | null
        // right side is string | undefined
        m.usage_ref.input ===
          sanitizeModuleInput(
            routerProps.input,
            serviceModulesQuery.data.core_input_name,
          ),
    );
  });

  createEffect(
    on(
      () => [serviceInstancesQuery.data, machinesQuery.data] as const,
      ([instances, machines]) => {
        // Wait for all queries to be ready
        if (!instances || !machines) return;
        const instance = instances[routerProps.id || routerProps.name];

        set("roles", {});
        if (!instance) {
          set("action", "create");
          return;
        }

        for (const role of Object.keys(instance.roles || {})) {
          // Get Role members
          const roleMembers = getRoleMembers(instance, machines, role);
          set("roles", role, roleMembers);
        }
        set("action", "update");
      },
    ),
  );

  const currentModuleRoles = createMemo(() => {
    const module = selectedModule();
    if (!module) return [];
    return Object.keys(module.info.roles).map((role) => ({
      role,
      members: store.roles?.[role] || [],
    }));
  });

  const tagsQuery = useTags(useClanURI());

  const options = useOptions(tagsQuery, machinesQuery);

  const handleSubmit = (values: RolesForm) => {
    const roles: Record<string, RoleType> = Object.fromEntries(
      Object.entries(store.roles).map(([key, value]) => [
        key,
        {
          machines: Object.fromEntries(
            value.filter((v) => v.type === "machine").map((v) => [v.label, {}]),
          ),
          tags: Object.fromEntries(
            value.filter((v) => v.type === "tag").map((v) => [v.label, {}]),
          ),
        },
      ]),
    );
    store.handleSubmit(
      {
        name: values.instanceName,
        module: {
          name: routerProps.name,
          input: sanitizeModuleInput(
            routerProps.input,
            serviceModulesQuery.data?.core_input_name || "clan-core",
          ),
        },
        roles,
      },
      store.action,
    );
  };

  return (
    <Form onSubmit={handleSubmit}>
      <div class={cx(styles.header, styles.backgroundAlt)}>
        <div class="overflow-hidden rounded-sm">
          <Icon icon="Services" size={36} inverted />
        </div>
        <div class="flex flex-col">
          <Typography hierarchy="body" size="s" weight="medium" inverted>
            {routerProps.name}
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
          color="primary"
          ghost
          size="s"
          in="ConfigureService"
          onClick={() => store.close()}
        />
      </div>
      <div class={styles.content}>
        <Show
          when={serviceModulesQuery.data && store.roles}
          fallback={<div>Loading...</div>}
        >
          <For each={currentModuleRoles()}>
            {(role) => {
              return (
                <TagSelect<TagType>
                  label={role.role}
                  renderItem={(item: TagType) => (
                    <Tag
                      inverted
                      icon={(tag) => (
                        <Icon
                          icon={item.type === "machine" ? "Machine" : "Tag"}
                          size="0.5rem"
                          inverted={tag.inverted}
                        />
                      )}
                    >
                      {item.label}
                    </Tag>
                  )}
                  values={role.members}
                  options={options()}
                  onClick={() => {
                    set("currentRole", role.role);
                    stepper.next();
                  }}
                />
              );
            }}
          </For>
        </Show>
      </div>
      <div class={cx(styles.footer, styles.backgroundAlt)}>
        <Button
          hierarchy="secondary"
          type="submit"
          loading={!serviceInstancesQuery.data}
        >
          <Show when={serviceInstancesQuery.data}>
            {(d) => (
              <>
                <Show
                  when={Object.keys(d()).includes(routerProps.id)}
                  fallback={"Add Service"}
                >
                  Save Changes
                </Show>
              </>
            )}
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
  const stepper = useStepper<ServiceSteps>();
  const [store, set] = getStepStore<ServiceStoreType>(stepper);

  const [members, setMembers] = createSignal<TagType[]>(
    store.roles?.[store.currentRole || ""] || [],
  );

  const clanUri = useClanURI();
  const machinesQuery = useMachinesQuery(clanUri);

  const lastClickedMachine = useMachineClick();

  createEffect(
    on(members, (m) => {
      clearAllHighlights();
      setHighlightGroups({
        [store.currentRole as string]: new Set(
          m.flatMap((m) => {
            if (m.type === "machine") return m.label;

            return m.members;
          }),
        ),
      });
    }),
  );

  onMount(() => {
    setHighlightGroups(() => ({}));
  });

  createEffect(
    on(lastClickedMachine, (machine) => {
      // const machine = lastClickedMachine();
      const currentMembers = members();
      if (!machine) return;

      const machineTagName = "m_" + machine;

      const existing = currentMembers.find((m) => m.value === machineTagName);
      if (existing) {
        // Remove
        setMembers(currentMembers.filter((m) => m.value !== machineTagName));
      } else {
        // Add
        setMembers([
          ...currentMembers,
          { value: machineTagName, label: machine, type: "machine" },
        ]);
      }
    }),
  );

  const tagsQuery = useTags(useClanURI());

  const options = useOptions(tagsQuery, machinesQuery);

  const handleSubmit = () => {
    if (!store.currentRole) return;

    if (!store.roles) {
      set("roles", {});
    }
    set("roles", (r) => ({ ...r, [store.currentRole as string]: members() }));
    stepper.setActiveStep("view:members");
  };

  return (
    <form onSubmit={() => handleSubmit()}>
      <div class={cx(styles.backgroundAlt, "rounded-md")}>
        <div class="flex w-full flex-col ">
          <SearchMultiple<TagType>
            values={members()}
            options={options()}
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
                  Select {store.currentRole}
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
                    {item.label}
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
                        {tag().members.length}
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
            onChange={(selection) => {
              setMembers(selection);
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
    content: ConfigureService,
  },
  {
    id: "select:members",
    content: ConfigureRole,
  },
  { id: "settings", content: () => <div>Adjust settings here.</div> },
] as const;

export type ServiceSteps = typeof steps;

interface ServiceWorkflowProps {
  initialStep?: ServiceSteps[number]["id"];
  initialStore?: Partial<ServiceStoreType>;
  onClose: () => void;
  handleSubmit: SubmitServiceHandler;
}

export const ServiceWorkflow = (props: ServiceWorkflowProps) => {
  const stepper = createStepper(
    { steps },
    {
      initialStep: props.initialStep || "view:members",
      initialStoreData: {
        ...props.initialStore,
        close: props.onClose,
        handleSubmit: props.handleSubmit,
      } satisfies Partial<ServiceStoreType>,
    },
  );

  createEffect(() => {
    if (stepper.currentStep().id !== "select:members") {
      clearAllHighlights();
    }
  });

  return (
    <div class="absolute bottom-full left-1/2 mb-2 -translate-x-1/2">
      <StepperProvider stepper={stepper}>
        <div class="w-[30rem]">{stepper.currentStep().content()}</div>
      </StepperProvider>
    </div>
  );
};
