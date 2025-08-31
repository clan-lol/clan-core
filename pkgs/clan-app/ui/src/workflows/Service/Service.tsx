import {
  createStepper,
  getStepStore,
  StepperProvider,
  useStepper,
} from "@/src/hooks/stepper";
import { useClanURI } from "@/src/hooks/clan";
import {
  MachinesQuery,
  ServiceModules,
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
  For,
  JSX,
  Show,
  on,
  onMount,
} from "solid-js";
import { Search } from "@/src/components/Search/Search";
import Icon from "@/src/components/Icon/Icon";
import { Combobox } from "@kobalte/core/combobox";
import { Typography } from "@/src/components/Typography/Typography";
import { TagSelect } from "@/src/components/Search/TagSelect";
import { Tag } from "@/src/components/Tag/Tag";
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
  highlightGroups,
  setHighlightGroups,
} from "@/src/scene/highlightStore";
import { useClickOutside } from "@/src/hooks/useClickOutside";

type ModuleItem = ServiceModules["modules"][number];

interface Module {
  value: string;
  label: string;
  raw: ModuleItem;
}

const SelectService = () => {
  const clanURI = useClanURI();
  const stepper = useStepper<ServiceSteps>();

  const serviceModulesQuery = useServiceModules(clanURI);
  const serviceInstancesQuery = useServiceInstances(clanURI);
  const machinesQuery = useMachinesQuery(clanURI);

  const [moduleOptions, setModuleOptions] = createSignal<Module[]>([]);
  createEffect(() => {
    if (serviceModulesQuery.data && serviceInstancesQuery.data) {
      setModuleOptions(
        serviceModulesQuery.data.modules.map((currService) => ({
          value: `${currService.usage_ref.name}:${currService.usage_ref.input}`,
          label: currService.usage_ref.name,
          raw: currService,
        })),
      );
    }
  });
  const [store, set] = getStepStore<ServiceStoreType>(stepper);

  return (
    <Search<Module>
      loading={serviceModulesQuery.isLoading}
      height="13rem"
      onChange={(module) => {
        if (!module) return;

        set("module", {
          name: module.raw.usage_ref.name,
          input: module.raw.usage_ref.input,
          raw: module.raw,
        });
        // TODO: Ideally we need to ask
        // - create new
        // - update existing (and select which one)

        // For now:
        // Create a new instance, if there are no instances yet
        // Update the first instance, if there is one
        if (module.raw.instance_refs.length === 0) {
          set("action", "create");
        } else {
          if (!serviceInstancesQuery.data) return;
          if (!machinesQuery.data) return;
          set("action", "update");

          const instanceName = module.raw.instance_refs[0];
          const instance = serviceInstancesQuery.data[instanceName];
          console.log("Editing existing instance", module);

          for (const role of Object.keys(instance.roles || {})) {
            const tags = Object.keys(instance.roles?.[role].tags || {});
            const machines = Object.keys(instance.roles?.[role].machines || {});

            const machineTags = machines.map((m) => ({
              value: "m_" + m,
              label: m,
              type: "machine" as const,
            }));
            const tagsTags = tags.map((t) => {
              return {
                value: "t_" + t,
                label: t,
                type: "tag" as const,
                members: Object.entries(machinesQuery.data || {})
                  .filter(([_, m]) => m.tags?.includes(t))
                  .map(([k]) => k),
              };
            });
            console.log("Members for role", role, [
              ...machineTags,
              ...tagsTags,
            ]);
            if (!store.roles) {
              set("roles", {});
            }
            const roleMembers = [...machineTags, ...tagsTags].sort((a, b) =>
              a.label.localeCompare(b.label),
            );
            set("roles", role, roleMembers);
            console.log("set", store.roles);
          }
          // Initialize the roles with the existing members
        }

        stepper.next();
      }}
      options={moduleOptions()}
      renderItem={(item, opts) => {
        return (
          <div class="flex items-center justify-between gap-2 overflow-hidden rounded-md px-2 py-1 pr-4">
            <div class="flex size-8 shrink-0 items-center justify-center rounded-md bg-white">
              <Icon icon="Code" />
            </div>
            <div class="flex w-full flex-col">
              <Combobox.ItemLabel class="flex gap-1.5">
                <Show when={item.raw.instance_refs.length > 0}>
                  <div class="flex items-center rounded bg-[#76FFA4] px-1 py-0.5">
                    <Typography hierarchy="label" weight="bold" size="xxs">
                      Added
                    </Typography>
                  </div>
                </Show>
                <Typography hierarchy="body" size="s" weight="medium" inverted>
                  {item.label}
                </Typography>
              </Combobox.ItemLabel>
              <Typography
                hierarchy="body"
                size="xxs"
                weight="normal"
                color="quaternary"
                inverted
                class="flex justify-between"
              >
                <span class="inline-block max-w-80 truncate align-middle">
                  {item.raw.info.manifest.description}
                </span>
                <span class="inline-block max-w-32 truncate align-middle">
                  <Show when={!item.raw.native} fallback="by clan-core">
                    by {item.raw.usage_ref.input}
                  </Show>
                </span>
              </Typography>
            </div>
          </div>
        );
      }}
    />
  );
};

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
        .filter(([_, v]) => v.tags?.includes(tag))
        .map(([k]) => k),
    }));

    return [...machineOptions, ...tagOptions].sort((a, b) =>
      a.label.localeCompare(b.label),
    );
  });

interface RolesForm extends FieldValues {
  roles: Record<string, string[]>;
  instanceName: string;
}
const ConfigureService = () => {
  const stepper = useStepper<ServiceSteps>();
  const [store, set] = getStepStore<ServiceStoreType>(stepper);

  const [formStore, { Form, Field }] = createForm<RolesForm>({
    initialValues: {
      // Default to the module name, until we support multiple instances
      instanceName: store.module.name,
    },
  });

  const machinesQuery = useMachinesQuery(useClanURI());
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
          name: store.module.name,
          input: store.module.input,
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
            {store.module.name}
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
          class="ml-auto"
          onClick={store.close}
        />
      </div>
      <div class={styles.content}>
        <For each={Object.keys(store.module.raw?.info.roles || {})}>
          {(role) => {
            const values = store.roles?.[role] || [];
            return (
              <TagSelect<TagType>
                label={role}
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
                values={values}
                options={options()}
                onClick={() => {
                  set("currentRole", role);
                  stepper.next();
                }}
              />
            );
          }}
        </For>
      </div>
      <div class={cx(styles.footer, styles.backgroundAlt)}>
        <BackButton ghost hierarchy="primary" class="mr-auto" />

        <Button hierarchy="secondary" type="submit">
          <Show when={store.action === "create"}>Add Service</Show>
          <Show when={store.action === "update"}>Save Changes</Show>
        </Button>
      </div>
    </Form>
  );
};

type TagType =
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

  const lastClickedMachine = useMachineClick();

  createEffect(() => {
    console.log("Current role", store.currentRole, members());
    clearAllHighlights();
    setHighlightGroups({
      [store.currentRole as string]: new Set(
        members().flatMap((m) => {
          if (m.type === "machine") return m.label;

          return m.members;
        }),
      ),
    });

    console.log("now", highlightGroups);
  });
  onMount(() => setHighlightGroups(() => ({})));

  createEffect(
    on(lastClickedMachine, (machine) => {
      // const machine = lastClickedMachine();
      const currentMembers = members();
      console.log("Clicked machine", machine, currentMembers);
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

  const machinesQuery = useMachinesQuery(useClanURI());
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
                <BackButton
                  ghost
                  size="xs"
                  hierarchy="primary"
                  // onClick={() => clearAllHighlights()}
                />
                <Typography
                  hierarchy="body"
                  size="s"
                  weight="medium"
                  inverted
                  class="capitalize"
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
                  class="ml-auto"
                  icon={item.type === "machine" ? "Machine" : "Tag"}
                  color="quaternary"
                  inverted
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
    id: "select:service",
    content: SelectService,
  },
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

// TODO: Ideally we would impot this from a backend model package
export interface InventoryInstance {
  name: string;
  module: {
    name: string;
    input?: string | null;
  };
  roles: Record<string, RoleType>;
}

interface RoleType {
  machines: Record<string, { settings?: unknown }>;
  tags: Record<string, unknown>;
}

export interface ServiceStoreType {
  module: {
    name: string;
    input?: string | null;
    raw?: ModuleItem;
  };
  roles: Record<string, TagType[]>;
  currentRole?: string;
  close: () => void;
  handleSubmit: SubmitServiceHandler;
  action: "create" | "update";
}

export type SubmitServiceHandler = (
  values: InventoryInstance,
  action: "create" | "update",
) => void | Promise<void>;

interface ServiceWorkflowProps {
  initialStep?: ServiceSteps[number]["id"];
  initialStore?: Partial<ServiceStoreType>;
  onClose?: () => void;
  handleSubmit: SubmitServiceHandler;
  rootProps?: JSX.HTMLAttributes<HTMLDivElement>;
}

export const ServiceWorkflow = (props: ServiceWorkflowProps) => {
  const stepper = createStepper(
    { steps },
    {
      initialStep: props.initialStep || "select:service",
      initialStoreData: {
        ...props.initialStore,
        close: () => props.onClose?.(),
        handleSubmit: props.handleSubmit,
      } satisfies Partial<ServiceStoreType>,
    },
  );
  createEffect(() => {
    if (stepper.currentStep().id !== "select:members") {
      clearAllHighlights();
    }
  });

  let ref: HTMLDivElement;
  useClickOutside(
    () => ref,
    () => {
      if (stepper.currentStep().id === "select:service") props.onClose?.();
    },
  );
  return (
    <div
      ref={(e) => (ref = e)}
      id="add-service"
      class="absolute bottom-full left-1/2 mb-2 -translate-x-1/2"
      {...props.rootProps}
    >
      <StepperProvider stepper={stepper}>
        <div class="w-[30rem]">{stepper.currentStep().content()}</div>
      </StepperProvider>
    </div>
  );
};
