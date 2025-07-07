import { TagProps } from "@/src/components/v2/Tag/Tag";
import { Meta, StoryObj } from "@kachurun/storybook-solid";
import { fn } from "storybook/test";
import {
  Modal,
  ModalContext,
  ModalProps,
} from "@/src/components/v2/Modal/Modal";
import { Fieldset } from "@/src/components/v2/Form/Fieldset";
import { TextInput } from "@/src/components/v2/Form/TextInput";
import { TextArea } from "@/src/components/v2/Form/TextArea";
import { Checkbox } from "@/src/components/v2/Form/Checkbox";
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
    children: ({ close }: ModalContext) => (
      <form class="flex flex-col gap-5">
        <Fieldset legend="General">
          {(props) => (
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
