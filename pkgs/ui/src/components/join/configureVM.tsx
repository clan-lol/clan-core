import { FormValues } from "@/views/joinPrequel";
import { UseFormReturn } from "react-hook-form";

interface VmDetailsProps {
  formHooks: UseFormReturn<FormValues, any, undefined>;
}

export const ConfigureVM = (props: VmDetailsProps) => {
  return <div className="grid grid-cols-4 gap-y-10"></div>;
};
