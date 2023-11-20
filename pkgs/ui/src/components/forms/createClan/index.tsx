import CopyAllIcon from "@mui/icons-material/CopyAll";
import SaveAltIcon from "@mui/icons-material/SaveAlt";
import {
  Button,
  InputAdornment,
  LinearProgress,
  TextField,
} from "@mui/material";
import { Controller, UseFormReturn } from "react-hook-form";

export type CreateFormValues = {
  flakeTemplateUrl: string;
  flakeDir: string;
};

interface CreateClanProps {
  confirmAdornment?: React.ReactNode;
  methods: UseFormReturn<CreateFormValues>;
}

export const CreateClan = (props: CreateClanProps) => {
  const { methods } = props;
  const {
    control,
    formState: { isSubmitting },
  } = methods;
  return (
    <div>
      <Controller
        name="flakeTemplateUrl"
        control={control}
        render={({ field, fieldState }) => (
          <TextField
            id="flakeTemplateUrl"
            error={Boolean(fieldState.error)}
            label="Clan Template"
            fullWidth
            variant="standard"
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <CopyAllIcon />
                </InputAdornment>
              ),
            }}
            helperText={fieldState.error?.message}
            {...field}
          />
        )}
      />
      <Controller
        name="flakeDir"
        control={control}
        render={({ field, fieldState }) => (
          <TextField
            id="flakeDir"
            error={Boolean(fieldState.error)}
            label="Directory"
            fullWidth
            variant="standard"
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <SaveAltIcon />
                </InputAdornment>
              ),
            }}
            helperText={fieldState.error?.message}
            {...field}
          />
        )}
      />
      <Button type="submit">Create</Button>
      {isSubmitting && <LinearProgress />}
    </div>
  );
};
