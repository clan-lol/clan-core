import styles from "./ClanSettingsModal.module.css";
import { Modal } from "@/src/components/Modal/Modal";
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
import { Alert } from "@/src/components/Alert/Alert";
import { useClanContext } from "../../Context/ClanContext";
import { ClanData } from "@/src/models";
import { JSONSchema } from "json-schema-typed";

const schema = v.object({
  name: v.string(),
  description: v.optional(v.string()),
  icon: v.optional(v.string()),
});

export interface ClanSettingsModalProps {
  onClose: () => void;
}

type FieldNames = "name" | "description" | "icon";

export const ClanSettingsModal = (props: ClanSettingsModalProps) => {
  const [clan, { updateClanData, removeClan }] = useClanContext()!;
  const [saving, setSaving] = createSignal(false);

  const [formStore, { Form, Field }] = createForm<ClanData>({
    initialValues: clan().data,
    validate: valiForm<ClanData>(schema),
  });

  const readOnly = (name: FieldNames) => clan().dataSchema[name]?.readonly;

  const onSubmit: SubmitHandler<ClanData> = async (values, event) => {
    setSaving(true);
    // TODO: once the backend supports partial update, only pass in changed data
    await updateClanData({
      ...clan().data,
      ...values,
    });
    setSaving(false);
    props.onClose();
  };

  const errorMessage = (): Maybe<string> => {
    const formErrors = getErrors(formStore);

    const firstFormError = Object.values(formErrors).find(
      (value) => value,
    ) as Maybe<string>;

    return firstFormError || formStore.response.message;
  };

  const [removeValue, setRemoveValue] = createSignal("");

  const removeDisabled = () => removeValue() !== clan().data.name;

  const onRemove = () => {
    removeClan();
  };

  return (
    <Modal
      class={styles.modal}
      open
      title="Settings"
      onClose={props.onClose}
      wrapContent={(props) => <Form onSubmit={onSubmit}>{props.children}</Form>}
      metaHeader={() => (
        <div class={styles.header}>
          <Typography
            hierarchy="label"
            family="mono"
            size="default"
            weight="medium"
          >
            {clan().data.name}
          </Typography>
          <Button hierarchy="primary" size="s" type="submit" loading={saving()}>
            Save
          </Button>
        </div>
      )}
    >
      <div class={styles.content}>
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
                  clan().dataSchema,
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
                  clan().dataSchema,
                  "A description of this Clan",
                )}
                orientation="horizontal"
                autoResize={true}
                minRows={2}
                maxRows={4}
                input={{
                  ...input,
                  placeholder: "No description",
                }}
              />
            )}
          </Field>
        </Fieldset>

        <div class={styles.remove}>
          <div class={styles.clanInput}>
            <TextInput
              orientation="horizontal"
              onChange={setRemoveValue}
              input={{
                value: removeValue(),
                placeholder: "Enter the name of this Clan",
                onKeyDown: (event) => {
                  if (event.key == "Enter" && !removeDisabled()) {
                    onRemove();
                  }
                },
              }}
            />
          </div>

          <Button
            hierarchy="primary"
            size="s"
            icon="Trash"
            disabled={removeDisabled()}
            onClick={onRemove}
          >
            Remove Clan
          </Button>
        </div>
      </div>
    </Modal>
  );
};
