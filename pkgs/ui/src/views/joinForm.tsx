import { Confirm } from "@/components/join/confirm";
import PublicIcon from "@mui/icons-material/Public";
import { Input, InputAdornment } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";

interface JoinFormProps {
  initialParams: {
    flakeUrl: string;
    flakeAttr: string;
  };
}
export const JoinForm = (props: JoinFormProps) => {
  const { initialParams } = props;
  const { control, formState, reset, getValues, watch } = useFormContext();

  return (
    <div>
      {watch("flakeUrl") || initialParams.flakeUrl ? (
        <Confirm
          handleBack={() => reset()}
          flakeUrl={
            formState.isSubmitted
              ? getValues("flakeUrl")
              : initialParams.flakeUrl
          }
          flakeAttr={initialParams.flakeAttr}
        />
      ) : (
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
              endAdornment={
                <InputAdornment position="end">
                  <PublicIcon />
                </InputAdornment>
              }
            />
          )}
        />
      )}
    </div>
  );
};
