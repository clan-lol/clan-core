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
import { GenericSchema, GenericSchemaAsync } from "valibot";
import { Typography } from "@/src/components/Typography/Typography";
import { Button } from "@/src/components/Button/Button";

import { Loader } from "../../components/Loader/Loader";
import { SidebarSection } from "./SidebarSection";

interface SidebarSectionFormProps<FormValues extends FieldValues> {
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

export function SidebarSectionForm<FormValues extends FieldValues>(
  props: SidebarSectionFormProps<FormValues>,
) {
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
      <SidebarSection
        title={props.title}
        controls={
          <>
            {editing() &&
              (formStore.submitting ? (
                <Loader />
              ) : (
                <Button
                  hierarchy="primary"
                  size="xs"
                  icon="Checkmark"
                  ghost
                  type="submit"
                >
                  Save
                </Button>
              ))}
            <Button
              hierarchy="primary"
              ghost
              size="xs"
              icon={editing() ? "Close" : "Edit"}
              onClick={editOrClose}
            />
          </>
        }
      >
        <Show when={editing() && formStore.dirty && errorMessage()}>
          <div class="mb-2.5" role="alert" aria-live="assertive">
            <Typography hierarchy="body" size="xs" inverted color="error">
              {errorMessage()}
            </Typography>
          </div>
        </Show>
        {props.children({ editing: editing(), Field, formStore })}
      </SidebarSection>
    </Form>
  );
}
