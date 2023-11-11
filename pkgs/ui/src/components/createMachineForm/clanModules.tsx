import { setMachineSchema } from "@/api/machine/machine";
import { useListClanModules } from "@/api/modules/modules";
import {
  Alert,
  AlertTitle,
  Divider,
  FormHelperText,
  Input,
  Typography,
} from "@mui/material";
import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import OutlinedInput from "@mui/material/OutlinedInput";
import Select, { SelectChangeEvent } from "@mui/material/Select";
import { Dispatch, SetStateAction, useEffect, useState } from "react";
import { Controller } from "react-hook-form";
import { toast } from "react-hot-toast";
import {
  CreateMachineForm,
  FormHooks,
  FormStepContentProps,
} from "./interfaces";

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
      width: 250,
    },
  },
};

interface IupdateSchema {
  clanName: string;
  modules: string[];
  formHooks: FormHooks;
  setSchemaError: Dispatch<SetStateAction<null | string>>;
}

const updateSchema = ({
  clanName,
  modules,
  formHooks,
  setSchemaError,
}: IupdateSchema) => {
  formHooks.setValue("isSchemaLoading", true);
  setMachineSchema(clanName, "example_machine", {
    clanImports: modules,
  })
    .then((response) => {
      if (response.statusText == "OK") {
        formHooks.setValue("schema", response.data.schema);
        setSchemaError(null);
      }
    })
    .catch((error) => {
      formHooks.setValue("schema", {});
      console.error({ error });
      setSchemaError(error.message);
      toast.error(`${error.message}`);
    })
    .finally(() => {
      formHooks.setValue("isSchemaLoading", false);
    });
};

type ClanModulesProps = FormStepContentProps;

const SchemaSuccessMsg = () => (
  <Alert severity="success">
    <AlertTitle>Success</AlertTitle>
    <Typography variant="subtitle2" sx={{ mt: 2 }}>
      Machine configuration schema successfully created.
    </Typography>
  </Alert>
);

interface SchemaErrorMsgProps {
  msg: string | null;
}

const SchemaErrorMsg = (props: SchemaErrorMsgProps) => (
  <Alert severity="error">
    <AlertTitle>Error</AlertTitle>
    <Typography variant="subtitle1" sx={{ mt: 2 }}>
      Machine configuration schema could not be created.
    </Typography>
    <Typography variant="subtitle2" sx={{ mt: 2 }}>
      {props.msg}
    </Typography>
  </Alert>
);

export default function ClanModules(props: ClanModulesProps) {
  const { clanName, formHooks } = props;
  const { data, isLoading } = useListClanModules(clanName);
  const [schemaError, setSchemaError] = useState<string | null>(null);
  const selectedModules = formHooks.watch("modules");
  useEffect(() => {
    updateSchema({
      clanName,
      modules: formHooks.watch("modules"),
      formHooks,
      setSchemaError,
    });

    // Only re-run if global clanName has changed
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [clanName]);
  const isSchemaLoading = formHooks.watch("isSchemaLoading");

  const handleChange = (
    event: SelectChangeEvent<CreateMachineForm["modules"]>,
  ) => {
    const {
      target: { value },
    } = event;
    const newValue = typeof value === "string" ? value.split(",") : value;
    formHooks.setValue("modules", newValue);

    updateSchema({
      clanName,
      modules: newValue,
      formHooks,
      setSchemaError,
    });
  };

  return (
    <div className="my-4 flex w-full flex-col justify-center px-2">
      <FormControl sx={{ my: 4 }} disabled={isLoading} required>
        <InputLabel>Machine name</InputLabel>
        <Controller
          name="name"
          control={formHooks.control}
          render={({ field }) => <Input {...field} />}
        />
        <FormHelperText>Choose a unique name for the machine.</FormHelperText>
      </FormControl>

      <Alert severity="info">
        <AlertTitle>Info</AlertTitle>
        Optionally select some modules —{" "}
        <strong>
          This will affect the configurable options in the next steps!
        </strong>
        <Typography variant="subtitle2" sx={{ mt: 2 }}>
          For example, if you add &quot;xfce&quot;, some configuration options
          for xfce will be added.
        </Typography>
      </Alert>

      <FormControl sx={{ my: 2 }} disabled={isLoading}>
        <InputLabel>Modules</InputLabel>
        <Select
          multiple
          value={selectedModules}
          onChange={handleChange}
          input={<OutlinedInput label="Modules" />}
          renderValue={(selected) => (
            <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5 }}>
              {selected.map((value) => (
                <Chip key={value} label={value} />
              ))}
            </Box>
          )}
          MenuProps={MenuProps}
        >
          {data?.data.clan_modules.map((name) => (
            <MenuItem key={name} value={name}>
              {name}
            </MenuItem>
          ))}
        </Select>
        <FormHelperText>
          (Optional) Select clan modules to be added.
        </FormHelperText>
      </FormControl>

      {!isSchemaLoading && <Divider flexItem sx={{ my: 4 }} />}
      {!isSchemaLoading &&
        (!schemaError ? (
          <SchemaSuccessMsg />
        ) : (
          <SchemaErrorMsg msg={schemaError} />
        ))}
    </div>
  );
}
