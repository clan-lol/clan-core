import { FieldValues, FormStore, ResponseData } from "@modular-forms/solid";
import { Show } from "solid-js";
import { type JSX } from "solid-js";

interface SelectInputProps<T extends FieldValues, R extends ResponseData> {
  formStore: FormStore<T, R>;
  value: string;
  options: JSX.Element;
  selectProps: JSX.HTMLAttributes<HTMLSelectElement>;
  label: JSX.Element;
  error?: string;
  required?: boolean;
  topRightLabel?: JSX.Element;
}

export function SelectInput<T extends FieldValues, R extends ResponseData>(
  props: SelectInputProps<T, R>,
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
        <Show when={props.topRightLabel}>
          <span class="label-text-alt">{props.topRightLabel}</span>
        </Show>
      </div>
      <select
        {...props.selectProps}
        required={props.required}
        class="select select-bordered w-full"
        value={props.value}
      >
        {props.options}
      </select>

      {props.error && (
        <span class="label-text-alt font-bold text-error">{props.error}</span>
      )}
    </label>
  );
}
