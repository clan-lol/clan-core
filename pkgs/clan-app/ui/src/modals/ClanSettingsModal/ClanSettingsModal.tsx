import cx from "classnames";
import styles from "./ClanSettingsModal.module.css";
import { Modal } from "@/src/components/Modal/Modal";
import { ClanDetails } from "@/src/hooks/queries";
import * as v from "valibot";
import {
  createForm,
  getErrors,
  Maybe,
  SubmitHandler,
  valiForm,
} from "@modular-forms/solid";
import { TextInput } from "@/src/components/Form/TextInput";
import { tooltipText } from "@/src/components/Form";
import { TextArea } from "@/src/components/Form/TextArea";
import { createSignal, Show, splitProps } from "solid-js";
import { Fieldset } from "@/src/components/Form/Fieldset";
import { Divider } from "@/src/components/Divider/Divider";
import { Typography } from "@/src/components/Typography/Typography";
import { Button } from "@/src/components/Button/Button";
import { callApi } from "@/src/hooks/api";
import { Alert } from "@/src/components/Alert/Alert";

const schema = v.object({
  name: v.pipe(v.optional(v.string())),
  description: v.nullish(v.string()),
  icon: v.pipe(v.nullish(v.string())),
});

export interface ClanSettingsModalProps {
  model: ClanDetails;
  onClose: () => void;
}

type FieldNames = "name" | "description" | "icon";
type FormValues = Pick<ClanDetails["details"], "name" | "description" | "icon">;

export const ClanSettingsModal = (props: ClanSettingsModalProps) => {
  const [saving, setSaving] = createSignal(false);

  const [formStore, { Form, Field }] = createForm<FormValues>({
    initialValues: props.model.details,
    validate: valiForm<FormValues>(schema),
  });

  const readOnly = (name: FieldNames) =>
    props.model.fieldsSchema[name]?.readonly ?? false;

  const handleSubmit: SubmitHandler<FormValues> = async (values, event) => {
    if (!formStore.dirty) {
      // nothing to save, just close the modal
      props.onClose();
      return;
    }

    // we only save stuff when the form is dirty
    setSaving(true);

    const call = callApi("set_clan_details", {
      options: {
        flake: {
          identifier: props.model.uri,
        },
        meta: {
          // todo we don't support icon field yet, so we mixin the original fields to stop the API from complaining
          // about deleting a field
          ...props.model.details,
          ...values,
        },
      },
    });

    const result = await call.result;

    setSaving(false);

    if (result.status == "error") {
      throw new Error(`Failed to save changes: ${result.errors[0].message}`);
    }

    if (result.status == "success") {
      props.onClose();
    }
  };

  const errorMessage = (): Maybe<string> => {
    const formErrors = getErrors(formStore);

    const firstFormError = Object.values(formErrors).find(
      (value) => value,
    ) as Maybe<string>;

    return firstFormError || formStore.response.message;
  };

  return (
    <Modal
      class={cx(styles.modal)}
      open
      title="Settings"
      onClose={props.onClose}
      wrapContent={(props) => (
        <Form onSubmit={handleSubmit}>{props.children}</Form>
      )}
      metaHeader={() => (
        <div class={cx(styles.header)}>
          <Typography
            hierarchy="label"
            family="mono"
            size="default"
            weight="medium"
          >
            {props.model.details.name}
          </Typography>
          <Button hierarchy="primary" size="s" type="submit" loading={saving()}>
            Save
          </Button>
        </div>
      )}
    >
      <Show when={errorMessage()}>
        <Alert type="error" title="Error" description={errorMessage()} />
      </Show>
      <Fieldset>
        <Field name="name">
          {(field, input) => (
            <TextInput
              {...field}
              value={field.value}
              label="Name"
              required
              readOnly={readOnly("name")}
              orientation="horizontal"
              input={input}
              tooltip={tooltipText(
                "name",
                props.model.fieldsSchema,
                "A unique identifier for this Clan",
              )}
            />
          )}
        </Field>
        <Divider />
        <Field name="description">
          {(field, input) => (
            <TextArea
              {...splitProps(field, ["value"])[1]}
              defaultValue={field.value ?? ""}
              label="Description"
              readOnly={readOnly("description")}
              tooltip={tooltipText(
                "description",
                props.model.fieldsSchema,
                "A description of this Clan",
              )}
              orientation="horizontal"
              input={{
                ...input,
                autoResize: true,
                minRows: 2,
                maxRows: 4,
                placeholder: "No description",
              }}
            />
          )}
        </Field>
      </Fieldset>
    </Modal>
  );
};
