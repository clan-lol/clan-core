import { Select as KSelect, SelectPortalProps } from "@kobalte/core/select";
import Icon from "../Icon/Icon";
import { Orienter } from "../Form/Orienter";
import { Label, LabelProps } from "../Form/Label";
import { createEffect, createSignal, JSX, Show, splitProps } from "solid-js";
import styles from "./Select.module.css";
import { Typography } from "../Typography/Typography";
import cx from "classnames";
import { useModalContext } from "../Modal/Modal";

export interface Option {
  value: string;
  label: string;
  disabled?: boolean;
}

export type SelectProps = {
  // Kobalte Select props, for modular forms
  name: string;
  placeholder?: string | undefined;
  noOptionsText?: string | undefined;
  value: string | undefined;
  error: string;
  required?: boolean | undefined;
  disabled?: boolean | undefined;
  ref: (element: HTMLSelectElement) => void;
  onInput: JSX.EventHandler<HTMLSelectElement, InputEvent>;
  onChange: JSX.EventHandler<HTMLSelectElement, Event>;
  onBlur: JSX.EventHandler<HTMLSelectElement, FocusEvent>;
  // Custom props
  orientation?: "horizontal" | "vertical";
  label?: Omit<LabelProps, "labelComponent" | "descriptionComponent">;
  portalProps?: Partial<SelectPortalProps>;
  zIndex?: number;
} & (
  | {
      // Sync options
      options: Option[];
      getOptions?: never;
    }
  | {
      // Async options
      getOptions: () => Promise<Option[]>;
      options?: never;
    }
);

export const Select = (props: SelectProps) => {
  const [root, selectProps] = splitProps(
    props,
    ["name", "placeholder", "required", "disabled"],
    ["placeholder", "ref", "onInput", "onChange", "onBlur"],
  );

  const zIndex = () => props.zIndex ?? 40;

  const [getValue, setValue] = createSignal<Option>();

  const [resolvedOptions, setResolvedOptions] = createSignal<Option[]>([]);

  // Internal loading state for async options
  const [loading, setLoading] = createSignal(false);
  createEffect(async () => {
    if (props.getOptions) {
      setLoading(true);
      try {
        const options = await props.getOptions();
        setResolvedOptions(options);
      } finally {
        setLoading(false);
      }
    } else if (props.options) {
      setResolvedOptions(props.options);
    }
  });

  const options = () => props.options ?? resolvedOptions();

  createEffect(() => {
    console.log("options,", options());
    setValue(options().find((option) => props.value === option.value));
  });

  const modalContext = useModalContext();
  const defaultMount =
    props.portalProps?.mount || modalContext?.portalRef || document.body;

  createEffect(() => {
    console.debug("Select component mounted at:", defaultMount);
  });
  return (
    <KSelect
      {...root}
      fitViewport={true}
      options={options()}
      sameWidth={true}
      gutter={0}
      multiple={false}
      value={getValue()}
      onChange={setValue}
      optionValue="value"
      optionTextValue="label"
      optionDisabled="disabled"
      validationState={props.error ? "invalid" : "valid"}
      itemComponent={(props) => (
        <KSelect.Item item={props.item} class="flex gap-1 p-2">
          <KSelect.ItemIndicator>
            <Icon icon="Checkmark" />
          </KSelect.ItemIndicator>
          <KSelect.ItemLabel>
            <Typography
              hierarchy="label"
              size="s"
              weight="bold"
              family="condensed"
              in="Select-item-label"
            >
              {props.item.rawValue.label}
            </Typography>
          </KSelect.ItemLabel>
        </KSelect.Item>
      )}
      placeholder={
        <Show
          when={!loading()}
          fallback={
            <Typography
              hierarchy="label"
              size="s"
              weight="bold"
              family="condensed"
              color="secondary"
              in="Select-item-label"
            >
              Loading...
            </Typography>
          }
        >
          <Show
            when={options().length > 0}
            fallback={
              <Typography
                hierarchy="label"
                size="s"
                weight="normal"
                family="condensed"
                color="secondary"
                in="Select-item-label"
              >
                {props.noOptionsText || "No options available"}
              </Typography>
            }
          >
            <Show when={props.placeholder}>
              <Typography
                hierarchy="label"
                size="s"
                weight="bold"
                family="condensed"
                in="Select-item-label"
              >
                {props.placeholder}
              </Typography>
            </Show>
          </Show>
        </Show>
      }
    >
      <Orienter orientation={props.orientation || "horizontal"}>
        <Label
          {...props.label}
          labelComponent={KSelect.Label}
          descriptionComponent={KSelect.Description}
          validationState={props.error ? "invalid" : "valid"}
        />
        <KSelect.HiddenSelect {...selectProps} />
        <KSelect.Trigger
          class={cx(styles.trigger)}
          style={{ "--z-index": zIndex() }}
          data-loading={loading() || undefined}
        >
          <KSelect.Value<Option>>
            {(state) => (
              <Typography
                hierarchy="label"
                size="s"
                weight="bold"
                family="condensed"
                in="Select-item-label"
              >
                {state.selectedOption().label}
              </Typography>
            )}
          </KSelect.Value>
          <KSelect.Icon
            as="button"
            class={styles.icon}
            data-loading={loading() || undefined}
          >
            <Icon icon="Expand" color="inherit" />
          </KSelect.Icon>
        </KSelect.Trigger>
      </Orienter>
      <KSelect.Portal mount={defaultMount} {...props.portalProps}>
        <KSelect.Content
          class={styles.options_content}
          style={{ "--z-index": zIndex() }}
        >
          <KSelect.Listbox>
            {() => (
              <KSelect.Trigger
                class={cx(styles.trigger)}
                style={{ "--z-index": zIndex() }}
                data-loading={loading() || undefined}
              >
                <KSelect.Value<Option>>
                  {(state) => (
                    <Typography
                      hierarchy="body"
                      size="xs"
                      weight="bold"
                      in="Select-item-label"
                    >
                      {state.selectedOption().label}
                    </Typography>
                  )}
                </KSelect.Value>
                <KSelect.Icon
                  as="button"
                  class={styles.icon}
                  data-loading={loading() || undefined}
                >
                  <Icon icon="Expand" color="inherit" />
                </KSelect.Icon>
              </KSelect.Trigger>
            )}
          </KSelect.Listbox>
        </KSelect.Content>
      </KSelect.Portal>
      {/* TODO: Display error next to the problem */}
      {/* <KSelect.ErrorMessage>{props.error}</KSelect.ErrorMessage> */}
    </KSelect>
  );
};
