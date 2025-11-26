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
import { removeClanURI } from "@/src/stores/clan";
import { useClanContext } from "@/src/contexts/ClanContext";

const schema = v.object({
  name: v.string(),
  description: v.optional(v.string()),
  icon: v.optional(v.string()),
});

export interface ClanSettingsModalProps {
  onClose: () => void;
}

type FieldNames = "name" | "description" | "icon";
type FormValues = Pick<ClanDetails["details"], "name" | "description" | "icon">;

export const ClanSettingsModal = (props: ClanSettingsModalProps) => {
  const { clans } = useClanContext()!;
  const activeClan = () => clans()?.active;
  const [saving, setSaving] = createSignal(false);

  const [formStore, { Form, Field }] = createForm<FormValues>({
    initialValues: activeClan()!,
    validate: valiForm<FormValues>(schema),
  });

  const readOnly = (name: FieldNames) => activeClan()?.schema[name]?.readonly;

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
          identifier: activeClan.path,
        },
        meta: {
          // todo we don't support icon field yet, so we mixin the original fields to stop the API from complaining
          // about deleting a field
          ...activeClan.data(),
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

  const [removeValue, setRemoveValue] = createSignal("");

  const removeDisabled = () => removeValue() !== activeClan.data()?.name;

  const onRemove = () => {
    removeClanURI(props.model.uri);
  };

  return (
    <Modal
      class={styles.modal}
      open
      title="Settings"
      onClose={props.onClose}
      wrapContent={(props) => (
        <Form onSubmit={handleSubmit}>{props.children}</Form>
      )}
      metaHeader={() => (
        <div class={styles.header}>
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
                  activeClan()!.schema,
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
                  activeClan()!.schema,
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
