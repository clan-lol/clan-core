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
  useServiceModules,
  useTags,
} from "@/src/hooks/queries";
import { createEffect, createMemo, createSignal, For, Show } from "solid-js";
import { Search } from "@/src/components/Search/Search";
import Icon from "@/src/components/Icon/Icon";
import { Combobox } from "@kobalte/core/combobox";
import { Typography } from "@/src/components/Typography/Typography";
import { Toolbar } from "@/src/components/Toolbar/Toolbar";
import { ToolbarButton } from "@/src/components/Toolbar/ToolbarButton";
import { TagSelect } from "@/src/components/Search/TagSelect";
import { Tag } from "@/src/components/Tag/Tag";
import { createForm, FieldValues, setValue } from "@modular-forms/solid";
import styles from "./Service.module.css";
import { TextInput } from "@/src/components/Form/TextInput";
import { Button } from "@/src/components/Button/Button";
import cx from "classnames";
import { BackButton } from "../Steps";
import { SearchMultiple } from "@/src/components/Search/MultipleSearch";

type ModuleItem = ServiceModules[number];

interface Module {
  value: string;
  input: string;
  label: string;
  description: string;
  raw: ModuleItem;
}

const SelectService = () => {
  const clanURI = useClanURI();
  const stepper = useStepper<ServiceSteps>();

  const serviceModulesQuery = useServiceModules(clanURI);

  const [moduleOptions, setModuleOptions] = createSignal<Module[]>([]);
  createEffect(() => {
    if (serviceModulesQuery.data) {
      setModuleOptions(
        serviceModulesQuery.data.map((m) => ({
          value: `${m.module.name}:${m.module.input}`,
          label: m.module.name,
          description: m.info.manifest.description,
          input: m.module.input || "clan-core",
          raw: m,
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
          name: module.raw.module.name,
          input: module.raw.module.input,
          raw: module.raw,
        });
        stepper.next();
      }}
      options={moduleOptions()}
      renderItem={(item) => {
        return (
          <div class="flex items-center justify-between gap-2 overflow-hidden rounded-md px-2 py-1 pr-4">
            <div class="flex size-8 items-center justify-center rounded-md bg-white">
              <Icon icon="Code" />
            </div>
            <div class="flex w-full flex-col">
              <Combobox.ItemLabel class="flex">
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
                <span>{item.description}</span>
                <span>by {item.input}</span>
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
    // initialValues: props.initialValues,
    initialValues: {
      instanceName: "backup-instance-1",
    },
  });

  const machinesQuery = useMachinesQuery(useClanURI());
  const tagsQuery = useTags(useClanURI());

  const options = useOptions(tagsQuery, machinesQuery);

  const handleSubmit = (values: RolesForm) => {
    console.log("Create service submitted with values:", values);
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
        <Button icon="Close" color="primary" ghost size="s" class="ml-auto" />
      </div>
      <div class={styles.content}>
        <For each={Object.keys(store.module.raw?.info.roles || {})}>
          {(role) => {
            const values = store.roles?.[role] || [];
            console.log("Role members:", role, values, "from", options());
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
        <Button hierarchy="secondary">Add Service</Button>
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

interface RoleMembers extends FieldValues {
  members: string[];
}
const ConfigureRole = () => {
  const stepper = useStepper<ServiceSteps>();
  const [store, set] = getStepStore<ServiceStoreType>(stepper);

  const [formStore, { Form, Field }] = createForm<RoleMembers>({
    initialValues: {
      members: [],
    },
  });

  const machinesQuery = useMachinesQuery(useClanURI());
  const tagsQuery = useTags(useClanURI());

  const options = useOptions(tagsQuery, machinesQuery);

  const handleSubmit = (values: RoleMembers) => {
    if (!store.currentRole) return;

    const members: TagType[] = values.members.map(
      (m) => options().find((o) => o.value === m)!,
    );

    if (!store.roles) {
      set("roles", {});
    }
    set("roles", (r) => ({ ...r, [store.currentRole as string]: members }));
    console.log("Roles form submitted ", members);

    stepper.setActiveStep("view:members");
  };

  return (
    <Form onSubmit={handleSubmit}>
      <div class={cx(styles.backgroundAlt, "rounded-md")}>
        <div class="flex w-full flex-col ">
          <Field name="members" type="string[]">
            {(field, input) => (
              <SearchMultiple<TagType>
                initialValues={store.roles?.[store.currentRole || ""] || []}
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
                      <Show
                        when={opts.selected}
                        fallback={<Icon icon="Code" />}
                      >
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
                  const newval = selection.map((s) => s.value);
                  setValue(formStore, field.name, newval);
                }}
              />
            )}
          </Field>
        </div>
        <div class={cx(styles.footer, styles.backgroundAlt)}>
          <Button hierarchy="secondary" type="submit">
            Confirm
          </Button>
        </div>
      </div>
    </Form>
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

export interface ServiceStoreType {
  module: {
    name: string;
    input: string;
    raw?: ModuleItem;
  };
  roles: Record<string, TagType[]>;
  currentRole?: string;
  close: () => void;
}

interface ServiceWorkflowProps {
  initialStep?: ServiceSteps[number]["id"];
  initialStore?: Partial<ServiceStoreType>;
}
export const ServiceWorkflow = (props: ServiceWorkflowProps) => {
  const [show, setShow] = createSignal(false);
  const stepper = createStepper(
    { steps },
    {
      initialStep: props.initialStep || "select:service",
      initialStoreData: {
        ...props.initialStore,
        close: () => setShow(false),
      } satisfies Partial<ServiceStoreType>,
    },
  );
  return (
    <>
      <div class="absolute bottom-4 left-1/2 flex -translate-x-1/2 flex-col items-center">
        <Show when={show()}>
          <div class="absolute bottom-full left-1/2 mb-2 -translate-x-1/2">
            <StepperProvider stepper={stepper}>
              <div class="w-[30rem]">{stepper.currentStep().content()}</div>
            </StepperProvider>
          </div>
        </Show>
        <div class="flex justify-center space-x-4">
          <Toolbar>
            <ToolbarButton
              onClick={() => setShow(!show())}
              description="Add new Service"
              name="modules"
              icon="Modules"
            />
          </Toolbar>
        </div>
      </div>
    </>
  );
};
