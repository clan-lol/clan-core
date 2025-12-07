import { BackButton, StepLayout } from "@/src/workflows/Steps";
import * as v from "valibot";
import { getStepStore, useStepper } from "@/src/hooks/stepper";
import {
  createForm,
  setValue,
  SubmitHandler,
  valiForm,
} from "@modular-forms/solid";
import { AddMachineSteps, AddMachineStoreType } from ".";
import { Fieldset } from "@/src/components/Form/Fieldset";
import { MachineTags } from "@/src/components/Form/MachineTags";
import { Button } from "@/src/components/Button/Button";
import { removeEmptyStrings } from "@/src/util";
import { useMachinesContext } from "../../Context/MachineContext";
import { useModalContext } from "../../Context/ModalContext";

const TagsSchema = v.object({
  tags: v.array(v.string()),
});

type TagsForm = v.InferInput<typeof TagsSchema>;

export const StepTags = () => {
  const [modal, { closeAddMachineModal }] = useModalContext<"addMachine">();
  const [, { addMachine }] = useMachinesContext();
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

    const machine = await addMachine({
      id: store.general.id,
      data: removeEmptyStrings({
        ...store.general,
        ...store.tags,
        deploy: store.deploy,
      }),
      position: modal.data.position,
    });
    closeAddMachineModal(machine);
  };

  return (
    <Form onSubmit={handleSubmit} class="h-full">
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
    </Form>
  );
};
