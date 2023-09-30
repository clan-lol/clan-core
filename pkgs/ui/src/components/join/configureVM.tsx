import {
  Button,
  InputAdornment,
  LinearProgress,
  ListSubheader,
  MenuItem,
  Select,
  Switch,
  TextField,
} from "@mui/material";
import { Controller, SubmitHandler, UseFormReturn } from "react-hook-form";
import { FlakeBadge } from "../flakeBadge/flakeBadge";
import { createVm, useGetVmLogs } from "@/api/default/default";
import { VmConfig } from "@/api/model";
import { Dispatch, SetStateAction, useState } from "react";
import { toast } from "react-hot-toast";

interface VmPropLabelProps {
  children: React.ReactNode;
}
const VmPropLabel = (props: VmPropLabelProps) => (
  <div className="col-span-4 flex items-center sm:col-span-1">
    {props.children}
  </div>
);

interface VmPropContentProps {
  children: React.ReactNode;
}
const VmPropContent = (props: VmPropContentProps) => (
  <div className="col-span-4 font-bold sm:col-span-3">{props.children}</div>
);

interface VmDetailsProps {
  vmConfig: VmConfig;
  formHooks: UseFormReturn<VmConfig, any, undefined>;
  setVmUuid: Dispatch<SetStateAction<string | null>>;
}

export const ConfigureVM = (props: VmDetailsProps) => {
  const { vmConfig, formHooks, setVmUuid } = props;
  const { control, handleSubmit } = formHooks;
  const { cores, flake_attr, flake_url, graphics, memory_size } = vmConfig;
  const [isStarting, setStarting] = useState(false);

  const onSubmit: SubmitHandler<VmConfig> = async (data) => {
    setStarting(true);
    console.log(data);
    const response = await createVm(data);
    const { uuid } = response?.data || null;

    setVmUuid(() => uuid);
    setStarting(false);
    if (response.statusText === "OK") {
      toast.success(("Joined @ " + uuid) as string);
    } else {
      toast.error("Could not join");
    }
  };

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="grid grid-cols-4 gap-y-10"
    >
      <div className="col-span-4">
        <ListSubheader>General</ListSubheader>
      </div>
      <VmPropLabel>Flake</VmPropLabel>
      <VmPropContent>
        <FlakeBadge flakeAttr={flake_attr} flakeUrl={flake_url} />
      </VmPropContent>
      <VmPropLabel>Machine</VmPropLabel>
      <VmPropContent>
        <Controller
          name="flake_attr"
          control={control}
          render={({ field }) => (
            <Select {...field} variant="standard" fullWidth>
              {["default", "vm1"].map((attr) => (
                <MenuItem value={attr} key={attr}>
                  {attr}
                </MenuItem>
              ))}
            </Select>
          )}
        />
      </VmPropContent>
      <div className="col-span-4">
        <ListSubheader>VM</ListSubheader>
      </div>
      <VmPropLabel>CPU Cores</VmPropLabel>
      <VmPropContent>
        <Controller
          name="cores"
          control={control}
          render={({ field }) => <TextField type="number" {...field} />}
        />
      </VmPropContent>
      <VmPropLabel>Graphics</VmPropLabel>
      <VmPropContent>
        <Controller
          name="graphics"
          control={control}
          render={({ field }) => (
            <Switch {...field} defaultChecked={vmConfig.graphics} />
          )}
        />
      </VmPropContent>
      <VmPropLabel>Memory Size</VmPropLabel>

      <VmPropContent>
        <Controller
          name="memory_size"
          control={control}
          render={({ field }) => (
            <TextField
              type="number"
              {...field}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">MiB</InputAdornment>
                ),
              }}
            />
          )}
        />
      </VmPropContent>

      <div className="col-span-4 grid items-center">
        {isStarting && <LinearProgress />}
        <Button type="submit" disabled={isStarting} variant="contained">
          Join Clan
        </Button>
      </div>
    </form>
  );
};
