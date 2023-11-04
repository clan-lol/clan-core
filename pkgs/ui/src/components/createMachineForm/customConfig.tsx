"use client";
import { useGetMachineSchema } from "@/api/machine/machine";
import { Check, Error } from "@mui/icons-material";
import {
  Box,
  Button,
  LinearProgress,
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
import { JSONSchema7 } from "json-schema";
import { useMemo, useRef } from "react";
import toast from "react-hot-toast";
import { FormStepContentProps } from "./interfaces";

interface PureCustomConfigProps extends FormStepContentProps {
  schema: JSONSchema7;
  initialValues: any;
}
export function CustomConfig(props: FormStepContentProps) {
  const { formHooks } = props;
  const { data, isLoading, error } = useGetMachineSchema(
    "defaultFlake",
    "mama",
  );
  // const { data, isLoading, error } = { data: {data:{schema: {
  //   title: 'Test form',
  //   type: 'object',
  //   properties: {
  //     name: {
  //       type: 'string',
  //     },
  //     age: {
  //       type: 'number',
  //     },
  //   },
  // }}}, isLoading: false, error: undefined }
  const schema = useMemo(() => {
    if (!isLoading && !error?.message && data?.data) {
      return data?.data.schema;
    }
    return {};
  }, [data, isLoading, error]);

  type ValueType = { default: any };
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
    [schema],
  );

  return isLoading ? (
    <LinearProgress variant="indeterminate" />
  ) : error?.message ? (
    <div>{error?.message}</div>
  ) : (
    <PureCustomConfig
      formHooks={formHooks}
      initialValues={initialValues}
      schema={schema}
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
  const { schema, formHooks } = props;
  const { setValue, watch } = formHooks;

  console.log({ schema });

  const configData = watch("config") as IChangeEvent<any>;

  console.log({ configData });

  const setConfig = (data: IChangeEvent<any>) => {
    console.log({ data });
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
        "Configuration is invalid. Please check the highlighted fields for details.",
      );
    } else {
      formHooks.clearErrors("config");
      toast.success("Config seems valid");
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
                Validate
              </Button>
            </div>
          ),
        },
      }}
    />
  );
}
