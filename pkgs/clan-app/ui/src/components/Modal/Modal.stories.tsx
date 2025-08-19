import { TagProps } from "@/src/components/Tag/Tag";
import { Meta, StoryObj } from "@kachurun/storybook-solid";
import { fn } from "storybook/test";
import { Modal, ModalProps } from "@/src/components/Modal/Modal";
import { Fieldset, FieldsetFieldProps } from "@/src/components/Form/Fieldset";
import { TextInput } from "@/src/components/Form/TextInput";
import { TextArea } from "@/src/components/Form/TextArea";
import { Checkbox } from "@/src/components/Form/Checkbox";
import { Button } from "../Button/Button";

const meta: Meta<ModalProps> = {
  title: "Components/Modal",
  component: Modal,
};

export default meta;

type Story = StoryObj<TagProps>;

export const Default: Story = {
  args: {
    title: "Example Modal",
    onClose: fn(),
    children: (
      <form class="flex flex-col gap-5">
        <Fieldset legend="General">
          {(props: FieldsetFieldProps) => (
            <>
              <TextInput
                {...props}
                label="First Name"
                size="s"
                required={true}
                input={{ placeholder: "Ron" }}
              />
              <TextInput
                {...props}
                label="Last Name"
                size="s"
                required={true}
                input={{ placeholder: "Burgundy" }}
              />
              <TextArea
                {...props}
                label="Bio"
                size="s"
                input={{ placeholder: "Tell us a bit about yourself", rows: 8 }}
              />
              <Checkbox
                {...props}
                size="s"
                label="Accept Terms"
                required={true}
              />
            </>
          )}
        </Fieldset>

        <div class="flex w-full items-center justify-end gap-4">
          <Button size="s" hierarchy="secondary" onClick={close}>
            Cancel
          </Button>
          <Button size="s" type="submit" hierarchy="primary" onClick={close}>
            Save
          </Button>
        </div>
      </form>
    ),
  },
};
