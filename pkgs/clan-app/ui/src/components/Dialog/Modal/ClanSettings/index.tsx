import * as v from "valibot";
import {
  createForm,
  getErrors,
  Maybe,
  SubmitHandler,
  valiForm,
} from "@modular-forms/solid";
import styles from "./ClanSettings.module.css";
import { TextInput } from "@/src/components/Form/TextInput";
import { tooltipText } from "@/src/components/Form";
import { TextArea } from "@/src/components/Form/TextArea";
import { Component, createSignal, Show, splitProps } from "solid-js";
import { Fieldset } from "@/src/components/Form/Fieldset";
import { Divider } from "@/src/components/Divider/Divider";
import { Button } from "@/src/components/Button/Button";
import { Alert } from "@/src/components/Alert/Alert";
import { ClanData, useClanContext } from "@/src/models";
import { ModalHeading } from "..";

const schema = v.object({
  name: v.string(),
  description: v.optional(v.string()),
  icon: v.optional(v.string()),
});

type FieldNames = "name" | "description" | "icon";

const ClanSettings: Component = () => {
  const [clan, { updateClanData, removeClan }] = useClanContext();
  const [saving, setSaving] = createSignal(false);

  const [formStore, { Form, Field }] = createForm<ClanData>({
    initialValues: clan().data,
    validate: valiForm<ClanData>(schema),
  });

  const readOnly = (name: FieldNames) => clan().dataSchema[name]?.readonly;

  const onSubmit: SubmitHandler<ClanData> = async (data, event) => {
    setSaving(true);
    await updateClanData(data);
    setSaving(false);
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
    <Form onSubmit={onSubmit}>
      <ModalHeading
        text={clan().data.name}
        tail={
          <Button hierarchy="primary" size="s" type="submit" loading={saving()}>
            Save
          </Button>
        }
      />
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
    </Form>
  );
};
export default ClanSettings;

export const title = "Settings";
