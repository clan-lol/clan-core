import {
  createStepper,
  getStepStore,
  StepperProvider,
  useStepper,
} from "@/src/hooks/stepper";
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
  Component,
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
import {
  clearAllHighlights,
  setHighlightGroups,
} from "@/src/components/MachineGraph/highlightStore";
import { getRoleMembers, RoleType, SubmitServiceHandler } from "./models";
import { TagSelect } from "@/src/components/Search/TagSelect";
import { Tag } from "@/src/components/Tag/Tag";
import {
  ClanMember,
  useClanContext,
  useMachinesContext,
  useServiceInstanceContext,
} from "@/src/models";

interface ServiceStoreType {
  roles: Record<string, TagType[]>;
  currentRole?: string;
  onClose(): void;
  onDone(): void;
  mode: "create" | "update";
}

const ServiceInstanceWorkflow: Component<{
  initialStep?: ServiceSteps[number]["id"];
  initialStore?: Partial<ServiceStoreType>;
  onClose?(): void;
  onDone?(): void;
}> = (props) => {
  const stepper = createStepper(
    { steps },
    {
      initialStep: props.initialStep || "view:members",
      initialStoreData: {
        ...props.initialStore,
        onClose: props.onClose,
        onDone: props.onDone,
      },
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
export default ServiceInstanceWorkflow;

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
const ConfigureServiceInstance = () => {
  const [serviceInstance] = useServiceInstanceContext();
  const [clan] = useClanContext();
  const stepper = useStepper<ServiceSteps>();

  const [store, setStore] = getStepStore<ServiceStoreType>(stepper);

  const [formStore, { Form, Field }] = createForm<RolesForm>({
    initialValues: {
      // Default to the module name, until we support multiple instances
      instanceName: serviceInstance().data.name,
    },
  });

  const onSubmit = (values: RolesForm) => {
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
    <Form onSubmit={onSubmit}>
      <div class={cx(styles.header, styles.backgroundAlt)}>
        <div class="overflow-hidden rounded-sm">
          <Icon icon="Services" size={36} inverted />
        </div>
        <div class="flex flex-col">
          <Typography hierarchy="body" size="s" weight="medium" inverted>
            {serviceInstance().data.name}
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
          onClick={() => store.onClose?.()}
        />
      </div>
      <div class={styles.content}>
        <For each={Object.entries(serviceInstance().data.roles)}>
          {([, role]) => {
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
                  setStore("currentRole", role.id);
                  stepper.next();
                }}
              />
            );
          }}
        </For>
      </div>
      <div class={cx(styles.footer, styles.backgroundAlt)}>
        <Button hierarchy="secondary" type="submit">
          <Show when={serviceInstance().isNew} fallback={"Save Changes"}>
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
  const stepper = useStepper<ServiceSteps>();
  const [store, set] = getStepStore<ServiceStoreType>(stepper);

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
    set("roles", (r) => ({
      ...r,
      [store.currentRole as string]: members(),
    }));
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
    content: ConfigureServiceInstance,
  },
  {
    id: "select:members",
    content: ConfigureRole,
  },
  { id: "settings", content: () => <div>Adjust settings here.</div> },
] as const;

type ServiceSteps = typeof steps;
