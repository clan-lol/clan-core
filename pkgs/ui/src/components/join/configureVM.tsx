import { useInspectFlakeAttrs } from "@/api/flake/flake";
import { FormValues } from "@/views/joinPrequel";
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
import { useEffect } from "react";
import { Controller, UseFormReturn } from "react-hook-form";
import { toast } from "react-hot-toast";
import { FlakeBadge } from "../flakeBadge/flakeBadge";

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
  formHooks: UseFormReturn<FormValues, any, undefined>;
}

type ClanError = {
  detail: {
    msg: string;
    loc: [];
  }[];
};

export const ConfigureVM = (props: VmDetailsProps) => {
  const { formHooks } = props;
  const { control, watch, setValue, formState } = formHooks;

  const { isLoading, data, error } = useInspectFlakeAttrs({
    url: watch("flakeUrl"),
  });

  useEffect(() => {
    if (!isLoading && data?.data) {
      setValue("flake_attr", data.data.flake_attrs[0] || "");
    }
  }, [isLoading, setValue, data]);
  if (error) {
    const msg =
      (error?.response?.data as unknown as ClanError)?.detail?.[0]?.msg ||
      error.message;

    toast.error(msg, {
      id: error.name,
    });
    return <div>{msg}</div>;
  }
  return (
    <div className="grid grid-cols-4 gap-y-10">
      <div className="col-span-4">
        <ListSubheader sx={{ bgcolor: "inherit" }}>General</ListSubheader>
      </div>
      <VmPropLabel>Flake</VmPropLabel>
      <VmPropContent>
        <FlakeBadge
          flakeAttr={watch("flake_attr")}
          flakeUrl={watch("flakeUrl")}
        />
      </VmPropContent>
      <VmPropLabel>Machine</VmPropLabel>
      <VmPropContent>
        {!isLoading && (
          <Controller
            name="flake_attr"
            control={control}
            defaultValue={data?.data.flake_attrs?.[0]}
            render={({ field }) => (
              <Select
                {...field}
                required
                variant="standard"
                fullWidth
                disabled={isLoading}
              >
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
        {formState.isSubmitting && <LinearProgress />}
        <Button
          autoFocus
          type="submit"
          disabled={formState.isSubmitting}
          variant="contained"
        >
          Join Clan
        </Button>
      </div>
    </div>
  );
};
