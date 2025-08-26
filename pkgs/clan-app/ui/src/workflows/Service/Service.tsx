import {
  createStepper,
  getStepStore,
  StepperProvider,
  useStepper,
} from "@/src/hooks/stepper";
import { BackButton, NextButton } from "../Steps";
import { useClanURI } from "@/src/hooks/clan";
import { ServiceModules, useServiceModules } from "@/src/hooks/queries";
import { createEffect, createSignal } from "solid-js";
import { Search } from "@/src/components/Search/Search";
import Icon from "@/src/components/Icon/Icon";
import { Combobox } from "@kobalte/core/combobox";
import { Typography } from "@/src/components/Typography/Typography";

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
      onChange={(module) => {
        if (!module) return;

        console.log("Module selected");
        set("module", {
          name: module.raw.module.name,
          input: module.raw.module.input,
        });
        stepper.next();
      }}
      options={moduleOptions()}
      renderItem={(item) => {
        return (
          <div class="flex items-center justify-between gap-2 rounded-md px-2 py-1 pr-4">
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

const steps = [
  {
    id: "select:service",
    content: SelectService,
  },
  {
    id: "select:members",
    content: () => <div>Configure your service here.</div>,
  },
  { id: "settings", content: () => <div>Adjust settings here.</div> },
] as const;

export type ServiceSteps = typeof steps;

export interface ServiceStoreType {
  module: {
    name: string;
    input: string;
  };
}

export const ServiceWorkflow = () => {
  const stepper = createStepper({ steps }, { initialStep: "select:service" });

  return (
    <StepperProvider stepper={stepper}>
      <BackButton />
      {stepper.currentStep().content()}
      <NextButton onClick={() => stepper.next()} />
    </StepperProvider>
  );
};
