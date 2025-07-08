import {
  TextField,
  TextFieldInputProps,
  TextFieldRootProps,
} from "@kobalte/core/text-field";

import cx from "classnames";
import { Label } from "./Label";
import { Button } from "../Button/Button";
import "./HostFileInput.css";
import { PolymorphicProps } from "@kobalte/core/polymorphic";
import { FieldProps } from "./Field";
import { Orienter } from "./Orienter";
import { createSignal } from "solid-js";

export type HostFileInputProps = FieldProps &
  TextFieldRootProps & {
    onSelectFile: () => Promise<string>;
    input?: PolymorphicProps<"input", TextFieldInputProps<"input">>;
  };

export const HostFileInput = (props: HostFileInputProps) => {
  const [value, setValue] = createSignal<string | undefined>(undefined);

  const selectFile = async () => {
    setValue(await props.onSelectFile());
  };

  return (
    <TextField
      class={cx("form-field", "host-file", props.size, props.orientation, {
        inverted: props.inverted,
        ghost: props.ghost,
      })}
      {...props}
      value={value()}
      onChange={setValue}
    >
      <Orienter orientation={props.orientation} align={"start"}>
        <Label
          labelComponent={TextField.Label}
          descriptionComponent={TextField.Description}
          {...props}
        />

        <TextField.Input {...props.input} hidden={true} />

        <Button
          hierarchy="secondary"
          size={props.size}
          startIcon="Folder"
          onClick={selectFile}
        >
          {value() ? value() : "No Selection"}
        </Button>
      </Orienter>
    </TextField>
  );
};
