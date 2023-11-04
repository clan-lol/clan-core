import { setMachineSchema } from "@/api/machine/machine";
import { useListClanModules } from "@/api/modules/modules";
import { Alert, AlertTitle, FormHelperText, Typography } from "@mui/material";
import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import OutlinedInput from "@mui/material/OutlinedInput";
import Select, { SelectChangeEvent } from "@mui/material/Select";
import { useEffect } from "react";
import { CreateMachineForm, FormStepContentProps } from "./interfaces";

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

type ClanModulesProps = FormStepContentProps;

export default function ClanModules(props: ClanModulesProps) {
  const { clanName, formHooks } = props;
  const { data, isLoading } = useListClanModules(clanName);

  const selectedModules = formHooks.watch("modules");

  useEffect(() => {
    setMachineSchema(clanName, "example_machine", {
      imports: [],
    }).then((response) => {
      if (response.statusText == "OK") {
        formHooks.setValue("schema", response.data.schema);
      }
    });
    formHooks.setValue("modules", []);
    // Only re-run if global clanName has changed
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [clanName]);

  const handleChange = (
    event: SelectChangeEvent<CreateMachineForm["modules"]>,
  ) => {
    const {
      target: { value },
    } = event;
    const newValue = typeof value === "string" ? value.split(",") : value;
    formHooks.setValue("modules", newValue);
    setMachineSchema(clanName, "example_machine", {
      imports: selectedModules,
    }).then((response) => {
      if (response.statusText == "OK") {
        formHooks.setValue("schema", response.data.schema);
      }
    });
  };
  return (
    <div className="my-4 flex w-full flex-col justify-center px-2">
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
    </div>
  );
}
