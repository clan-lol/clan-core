import { Input, InputAdornment, LinearProgress } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";

interface CreateFormProps {
  confirmAdornment?: React.ReactNode;
}

export const CreateForm = (props: CreateFormProps) => {
  const { confirmAdornment } = props;
  const {
    control,
    formState: { isSubmitting },
  } = useFormContext();
  return (
    <div>
      <Controller
        name="flakeUrl"
        control={control}
        render={({ field }) => (
          <Input
            disableUnderline
            placeholder="url"
            color="secondary"
            aria-required="true"
            {...field}
            required
            fullWidth
            startAdornment={
              <InputAdornment position="start">Clan</InputAdornment>
            }
          />
        )}
      />
      <Controller
        name="dest"
        control={control}
        render={({ field }) => (
          <Input
            sx={{ my: 2 }}
            placeholder="Location"
            color="secondary"
            aria-required="true"
            {...field}
            required
            fullWidth
            startAdornment={
              <InputAdornment position="start">Name</InputAdornment>
            }
            endAdornment={confirmAdornment}
          />
        )}
      />
      {isSubmitting && <LinearProgress />}
    </div>
  );
};
