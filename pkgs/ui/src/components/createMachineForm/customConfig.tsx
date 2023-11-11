"use client";
import { Check, Error } from "@mui/icons-material";
import {
  Box,
  Button,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper,
  Typography,
} from "@mui/material";
import { IChangeEvent } from "@rjsf/core";
import { Form } from "@rjsf/mui";
import {
  ErrorListProps,
  FormContextType,
  RJSFSchema,
  StrictRJSFSchema,
  TranslatableString,
} from "@rjsf/utils";
import validator from "@rjsf/validator-ajv8";
import { useMemo, useRef } from "react";
import toast from "react-hot-toast";
import { FormStepContentProps } from "./interfaces";

type ValueType = { default: any };
interface PureCustomConfigProps extends FormStepContentProps {
  initialValues: any;
}
export function CustomConfig(props: FormStepContentProps) {
  const { formHooks, clanName } = props;
  const schema = formHooks.watch("schema");

  const initialValues = useMemo(
    () =>
      Object.entries(schema?.properties || {}).reduce((acc, [key, value]) => {
        const init: any = (value as ValueType)?.default;
        if (init) {
          return {
            ...acc,
            [key]: init,
          };
        }
        return acc;
      }, {}),
    [schema]
  );

  return (
    <PureCustomConfig
      clanName={clanName}
      formHooks={formHooks}
      initialValues={initialValues}
    />
  );
}

function ErrorList<
  T = any,
  S extends StrictRJSFSchema = RJSFSchema,
  F extends FormContextType = any,
>({ errors, registry }: ErrorListProps<T, S, F>) {
  const { translateString } = registry;
  return (
    <Paper elevation={0}>
      <Box mb={2} p={2}>
        <Typography variant="h6">
          {translateString(TranslatableString.ErrorsLabel)}
        </Typography>
        <List dense={true}>
          {errors.map((error, i: number) => {
            return (
              <ListItem key={i}>
                <ListItemIcon>
                  <Error color="error" />
                </ListItemIcon>
                <ListItemText primary={error.stack} />
              </ListItem>
            );
          })}
        </List>
      </Box>
    </Paper>
  );
}

function PureCustomConfig(props: PureCustomConfigProps) {
  const { formHooks } = props;
  const { setValue, watch } = formHooks;
  const schema = watch("schema");
  console.log({ schema });

  const configData = watch("config") as IChangeEvent<any>;

  console.log({ configData });

  const setConfig = (data: IChangeEvent<any>) => {
    console.log("config changed", { data });
    setValue("config", data);
  };

  const formRef = useRef<any>();

  const validate = () => {
    const isValid: boolean = formRef?.current?.validateForm();
    console.log({ isValid }, formRef.current);
    if (!isValid) {
      formHooks.setError("config", {
        message: "invalid config",
      });
      toast.error(
        "Configuration is invalid. Please check the highlighted fields for details."
      );
    } else {
      formHooks.clearErrors("config");
      toast.success("Configuration is valid");
    }
  };

  return (
    <Form
      ref={formRef}
      onChange={setConfig}
      formData={configData.formData}
      acceptcharset="utf-8"
      schema={schema}
      validator={validator}
      liveValidate={true}
      templates={{
        // ObjectFieldTemplate:
        ErrorListTemplate: ErrorList,
        ButtonTemplates: {
          SubmitButton: () => (
            <div className="flex w-full items-center justify-center">
              <Button
                onClick={validate}
                startIcon={<Check />}
                variant="outlined"
                color="secondary"
              >
                Validate configuration
              </Button>
            </div>
          ),
        },
      }}
    />
  );
}
