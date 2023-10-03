import { ReactElement } from "react";
import { UseFormReturn } from "react-hook-form";

export type StepId = "template" | "modules" | "config" | "save";

export type CreateMachineForm = {
  name: string;
  config: any;
};

export type FormHooks = UseFormReturn<CreateMachineForm>;

export type FormStep = {
  id: StepId;
  label: string;
  content: FormStepContent;
};

export interface FormStepContentProps {
  formHooks: FormHooks;
}

export type FormStepContent = ReactElement<FormStepContentProps>;
