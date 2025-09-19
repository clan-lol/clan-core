import { createSignal, JSX, Show } from "solid-js";
import {
  createForm,
  FieldValues,
  FormStore,
  getErrors,
  Maybe,
  PartialValues,
  reset,
  SubmitHandler,
  valiForm,
} from "@modular-forms/solid";
import { OperationNames, SuccessData } from "@/src/hooks/api";
import { GenericSchema, GenericSchemaAsync } from "valibot";
import { Typography } from "@/src/components/Typography/Typography";
import { Button } from "@/src/components/Button/Button";

import "./SidebarSection.css";
import { Loader } from "../../components/Loader/Loader";

export interface SidebarSectionFormProps<FormValues extends FieldValues> {
  title: string;
  schema: GenericSchema<FormValues> | GenericSchemaAsync<FormValues>;
  initialValues: PartialValues<FormValues>;
  onSubmit: (values: FormValues) => Promise<void>;
  children: (ctx: {
    editing: boolean;
    Field: ReturnType<typeof createForm<FormValues>>[1]["Field"];
    formStore: FormStore<FormValues>;
  }) => JSX.Element;
}

export function SidebarSectionForm<
  T extends OperationNames,
  FormValues extends FieldValues = SuccessData<T> extends FieldValues
    ? SuccessData<T>
    : never,
>(props: SidebarSectionFormProps<FormValues>) {
  const [editing, setEditing] = createSignal(false);

  const [formStore, { Form, Field }] = createForm<FormValues>({
    initialValues: props.initialValues,
    validate: valiForm<FormValues>(props.schema),
  });

  const editOrClose = () => {
    if (editing()) {
      reset(formStore, props.initialValues);
      setEditing(false);
    } else {
      setEditing(true);
    }
  };

  const handleSubmit: SubmitHandler<FormValues> = async (values, event) => {
    console.log("Submitting SidebarForm", values);

    await props.onSubmit(values);
    setEditing(false);
  };

  const errorMessage = (): Maybe<string> => {
    const formErrors = getErrors(formStore);

    const firstFormError = Object.values(formErrors).find(
      (value) => value,
    ) as Maybe<string>;

    return firstFormError || formStore.response.message;
  };

  return (
    <Form onSubmit={handleSubmit}>
      <div class="sidebar-section">
        <div class="header">
          <Typography
            hierarchy="label"
            size="xs"
            family="mono"
            transform="uppercase"
            color="tertiary"
            inverted
          >
            {props.title}
          </Typography>
          <div class="controls h-4">
            {editing() && !formStore.submitting && (
              <Button
                hierarchy="primary"
                size="xs"
                icon="Checkmark"
                ghost
                type="submit"
              >
                Save
              </Button>
            )}
            {editing() && formStore.submitting && <Loader />}
            <Button
              hierarchy="primary"
              ghost
              size="xs"
              icon={editing() ? "Close" : "Edit"}
              onClick={editOrClose}
            />
          </div>
        </div>
        <div class="content">
          <Show when={editing() && formStore.dirty && errorMessage()}>
            <div class="mb-2.5" role="alert" aria-live="assertive">
              <Typography hierarchy="body" size="xs" inverted color="error">
                {errorMessage()}
              </Typography>
            </div>
          </Show>
          {props.children({ editing: editing(), Field, formStore })}
        </div>
      </div>
    </Form>
  );
}
