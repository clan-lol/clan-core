import { JSONSchema7 } from "json-schema";
import { ReactElement } from "react";
import { UseFormReturn } from "react-hook-form";

export type StepId = "template" | "modules" | "config" | "save";

export type CreateMachineForm = {
  name: string;
  config: any;
  modules: string[];
  schema: JSONSchema7;
};

export type FormHooks = UseFormReturn<CreateMachineForm>;

export type FormStep = {
  id: StepId;
  label: string;
  content: FormStepContent;
};

export interface FormStepContentProps {
  formHooks: FormHooks;
  clanName: string;
}

export type FormStepContent = ReactElement<FormStepContentProps>;
