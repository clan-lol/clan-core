import {
  BackButton,
  StepLayout,
} from "@/src/components/Steps";
import * as v from "valibot";
import { getStepStore, useStepper } from "@/src/components/Steps/stepper";
import {
  createForm,
  setValue,
  SubmitHandler,
  valiForm,
} from "@modular-forms/solid";
import styles from "./AddMachine.module.css";
import { AddMachineSteps, AddMachineStoreType } from ".";
import { Fieldset } from "@/src/components/Form/Fieldset";
import { MachineTags } from "@/src/components/Form/MachineTags";
import { Button } from "@/src/components/Button/Button";
import { removeEmptyStrings } from "@/src/util";
import { useMachinesContext, useUIContext } from "@/src/models";
import { Modal } from "@/src/models";
import ModalHeading from "../components/ModalHeading";

const TagsSchema = v.object({
  tags: v.array(v.string()),
});

type TagsForm = v.InferInput<typeof TagsSchema>;

export const StepTags = () => {
  const [ui, { closeModal }] = useUIContext();
  const modal = () => ui.modal as Extract<Modal, { type: "AddMachine" }>;
  const [, { createMachine }] = useMachinesContext();
  const stepSignal = useStepper<AddMachineSteps>();
  const [store, set] = getStepStore<AddMachineStoreType>(stepSignal);

  const [formStore, { Form, Field }] = createForm<TagsForm>({
    validate: valiForm(TagsSchema),
    initialValues: store.tags,
  });

  const handleSubmit: SubmitHandler<TagsForm> = async (values, event) => {
    set("tags", (s) => ({
      ...s,
      ...values,
    }));

    stepSignal.next();
    await createMachine(
      store.general.id,
      removeEmptyStrings({
        machineClass: store.general.machineClass,
        description: store.general.description,
        deploy: store.deploy,
        tags: store.tags.tags,
        position: modal().position,
      }),
    );
    closeModal();
  };

  return (
    <Form onSubmit={handleSubmit} class={styles.container}>
      <ModalHeading text="Tags" />
      <div class={styles.content}>
        <StepLayout
          body={
            <div class="flex flex-col gap-2">
              <Fieldset>
                <Field name="tags" type="string[]">
                  {(field, input) => (
                    <MachineTags
                      {...field}
                      required
                      orientation="horizontal"
                      defaultValue={field.value || []}
                      defaultOptions={[]}
                      onChange={(newVal) => {
                        // Workaround for now, until we manage to use native events
                        setValue(formStore, field.name, newVal);
                      }}
                    />
                  )}
                </Field>
              </Fieldset>
            </div>
          }
          footer={
            <div class="flex justify-between">
              <BackButton />
              <Button hierarchy="primary" type="submit" endIcon="Flash">
                Create Machine
              </Button>
            </div>
          }
        />
      </div>
    </Form>
  );
};
