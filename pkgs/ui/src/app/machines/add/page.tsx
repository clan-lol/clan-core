"use client";

import { useForm } from "react-hook-form";

import { JSONSchema7 } from "json-schema";
import { useMemo, useState } from "react";
import { schema } from "./schema";
import Form from "@rjsf/mui";
import validator from "@rjsf/validator-ajv8";
import { Button } from "@mui/material";

interface CreateMachineFormProps {
  schema: JSONSchema7;
  initialValues: any;
}

const defaultValues = Object.entries(schema.properties || {}).reduce(
  (acc, [key, value]) => {
    /*@ts-ignore*/
    const init: any = value?.default;
    if (init) {
      return {
        ...acc,
        [key]: init,
      };
    }
    return acc;
  },
  {},
);

function CreateMachineForm(props: CreateMachineFormProps) {
  const { schema, initialValues } = props;

  return (
    <Form
      acceptcharset="utf-8"
      // @ts-ignore
      extraErrors={{
        __errors: ["Global error; Server said no"],
        // @ts-ignore
        name: {
          __errors: ["Name is already in use"],
        },
      }}
      schema={schema}
      validator={validator}
      liveValidate={true}
      templates={{
        ButtonTemplates: {
          SubmitButton: (props) => (
            <Button type="submit" variant="contained" color="secondary">
              Create Machine
            </Button>
          ),
        },
      }}
    />
  );
}

export default function CreateMachine() {
  return <CreateMachineForm schema={schema} initialValues={defaultValues} />;
}
