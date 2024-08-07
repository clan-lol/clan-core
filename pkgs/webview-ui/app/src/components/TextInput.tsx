import { FieldValues, FormStore, ResponseData } from "@modular-forms/solid";
import { type JSX } from "solid-js";

interface TextInputProps<T extends FieldValues, R extends ResponseData> {
  formStore: FormStore<T, R>;
  value: string;
  inputProps: JSX.InputHTMLAttributes<HTMLInputElement>;
  label: JSX.Element;
  error?: string;
  required?: boolean;
  type?: string;
  inlineLabel?: JSX.Element;
}

export function TextInput<T extends FieldValues, R extends ResponseData>(
  props: TextInputProps<T, R>,
) {
  return (
    <label
      class="form-control w-full"
      aria-disabled={props.formStore.submitting}
    >
      <div class="label">
        <span
          class="label-text block"
          classList={{
            "after:ml-0.5 after:text-primary after:content-['*']":
              props.required,
          }}
        >
          {props.label}
        </span>
      </div>

      <div class="input input-bordered flex items-center gap-2">
        {props.inlineLabel}
        <input
          {...props.inputProps}
          value={props.value}
          type={props.type ? props.type : "text"}
          class="grow"
          classList={{
            "input-disabled": props.formStore.submitting,
          }}
          placeholder="name"
          required
          disabled={props.formStore.submitting}
        />
      </div>
      {props.error && (
        <span class="label-text-alt font-bold text-error">{props.error}</span>
      )}
    </label>
  );
}
