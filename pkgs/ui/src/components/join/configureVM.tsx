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
import { createVm, useInspectFlakeAttrs } from "@/api/default/default";
import { VmConfig } from "@/api/model";
import { Dispatch, SetStateAction, useEffect, useState } from "react";
import { toast } from "react-hot-toast";
import { useAppState } from "../hooks/useAppContext";

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
  <div className="col-span-4 sm:col-span-3">{props.children}</div>
);

interface VmDetailsProps {
  formHooks: UseFormReturn<VmConfig, any, undefined>;
  setVmUuid: Dispatch<SetStateAction<string | null>>;
}

export const ConfigureVM = (props: VmDetailsProps) => {
  const { formHooks, setVmUuid } = props;
  const { control, handleSubmit, watch, setValue } = formHooks;
  const [isStarting, setStarting] = useState(false);
  const { setAppState } = useAppState();
  const { isLoading, data } = useInspectFlakeAttrs({ url: watch("flake_url") });

  useEffect(() => {
    if (!isLoading && data?.data) {
      setValue("flake_attr", data.data.flake_attrs[0] || "");
    }
  }, [isLoading, setValue, data]);

  const onSubmit: SubmitHandler<VmConfig> = async (data) => {
    setStarting(true);
    console.log(data);
    const response = await createVm(data);
    const { uuid } = response?.data || null;

    setVmUuid(() => uuid);
    setStarting(false);
    if (response.statusText === "OK") {
      toast.success(("Joined @ " + uuid) as string);
      setAppState((s) => ({ ...s, isJoined: true }));
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
        <ListSubheader sx={{ bgcolor: "inherit" }}>General</ListSubheader>
      </div>
      <VmPropLabel>Flake</VmPropLabel>
      <VmPropContent>
        <FlakeBadge
          flakeAttr={watch("flake_attr")}
          flakeUrl={watch("flake_url")}
        />
      </VmPropContent>
      <VmPropLabel>Machine</VmPropLabel>
      <VmPropContent>
        {!isLoading && (
          <Controller
            name="flake_attr"
            control={control}
            render={({ field }) => (
              <Select
                {...field}
                required
                variant="standard"
                fullWidth
                disabled={isLoading}
              >
                {!data?.data.flake_attrs.includes("default") && (
                  <MenuItem value={"default"}>default</MenuItem>
                )}
                {data?.data.flake_attrs.map((attr) => (
                  <MenuItem value={attr} key={attr}>
                    {attr}
                  </MenuItem>
                ))}
              </Select>
            )}
          />
        )}
      </VmPropContent>
      <div className="col-span-4">
        <ListSubheader sx={{ bgcolor: "inherit" }}>VM</ListSubheader>
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
            <Switch {...field} defaultChecked={watch("graphics")} />
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
        <Button
          autoFocus
          type="submit"
          disabled={isStarting}
          variant="contained"
        >
          Join Clan
        </Button>
      </div>
    </form>
  );
};
