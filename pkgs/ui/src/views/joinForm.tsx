import { Confirm } from "@/components/join/confirm";
import { Input, InputAdornment } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";

interface JoinFormProps {
  confirmAdornment?: React.ReactNode;
  initialParams: {
    flakeUrl: string;
    flakeAttr: string;
  };
}
export const JoinForm = (props: JoinFormProps) => {
  const { initialParams, confirmAdornment } = props;
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
              startAdornment={
                <InputAdornment position="start">Clan</InputAdornment>
              }
              endAdornment={confirmAdornment}
            />
          )}
        />
      )}
    </div>
  );
};
