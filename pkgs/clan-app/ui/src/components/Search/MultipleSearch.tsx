import Icon from "../Icon/Icon";
import { Button } from "../Button/Button";
import styles from "./Search.module.css";
import { Combobox } from "@kobalte/core/combobox";
import {
  createEffect,
  createMemo,
  createSignal,
  For,
  JSX,
  Match,
  Switch,
} from "solid-js";
import { createVirtualizer, VirtualizerOptions } from "@tanstack/solid-virtual";
import { CollectionNode } from "@kobalte/core/*";
import cx from "classnames";
import { Loader } from "../Loader/Loader";

interface Option {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface ItemRenderOptions {
  selected: boolean;
  disabled: boolean;
}

export interface SearchMultipleProps<T> {
  values: T[]; // controlled values
  onChange: (values: T[]) => void;
  options: T[];
  renderItem: (item: T, opts: ItemRenderOptions) => JSX.Element;
  initialValues?: T[];
  placeholder?: string;
  virtualizerOptions?: Partial<VirtualizerOptions<Element, Element>>;
  height: string; // e.g. '14.5rem'
  headerClass?: string;
  headerChildren?: JSX.Element;
  loading?: boolean;
  loadingComponent?: JSX.Element;
  divider?: boolean;
}
export function SearchMultiple<T extends Option>(
  props: SearchMultipleProps<T>,
) {
  // Controlled input value, to allow resetting the input itself
  // const [values, setValues] = createSignal<T[]>(props.initialValues || []);
  const [inputValue, setInputValue] = createSignal<string>("");

  let inputEl: HTMLInputElement;

  let listboxRef: HTMLUListElement;

  // const [currentItems, setItems] = createSignal(ALL_MODULES_OPTIONS_FLAT);
  const [comboboxItems, setComboboxItems] = createSignal<CollectionNode<T>[]>(
    props.options.map((item) => ({
      rawValue: item,
    })) as CollectionNode<T>[],
  );

  // Create a reactive virtualizer that updates when items change
  const virtualizer = createMemo(() => {
    const items = comboboxItems();

    const newVirtualizer = createVirtualizer({
      count: items.length,
      getScrollElement: () => listboxRef,
      getItemKey: (index) => {
        const item = items[index];
        return item?.rawValue?.value || `item-${index}`;
      },
      estimateSize: () => 42,
      gap: 0,
      overscan: 5,
      ...props.virtualizerOptions,
    });

    return newVirtualizer;
  });
  createEffect(() => {
    console.log("multi values:", props.values);
  });
  return (
    <Combobox<T>
      multiple
      value={props.values}
      onChange={(values) => {
        // setValues(() => values);
        console.log("onChange", values);
        props.onChange(values);
      }}
      class={styles.searchContainer}
      placement="bottom-start"
      options={props.options}
      optionValue="value"
      optionTextValue="label"
      optionLabel="label"
      optionDisabled={"disabled"}
      sameWidth={true}
      open={true}
      gutter={7}
      modal={false}
      flip={false}
      virtualized={true}
      allowsEmptyCollection={true}
      closeOnSelection={false}
      triggerMode="manual"
      noResetInputOnBlur={true}
    >
      <Combobox.Control<T>
        class={cx(styles.searchHeader, props.headerClass || "bg-inv-3")}
      >
        {(state) => (
          <>
            {props.headerChildren}
            <div class={styles.inputContainer}>
              <Icon icon="Search" color="quaternary" />
              <Combobox.Input
                ref={(el) => {
                  inputEl = el;
                }}
                class={styles.searchInput}
                placeholder={props.placeholder}
                value={inputValue()}
                onChange={(e) => {
                  setInputValue(e.currentTarget.value);
                }}
              />
              <Button
                type="reset"
                hierarchy="primary"
                size="s"
                ghost
                icon="CloseCircle"
                onClick={() => {
                  state.clear();
                  setInputValue("");

                  // Dispatch an input event to notify combobox listeners
                  inputEl.dispatchEvent(
                    new Event("input", { bubbles: true, cancelable: true }),
                  );
                }}
              />
            </div>
          </>
        )}
      </Combobox.Control>
      <Combobox.Listbox<T>
        ref={(el) => {
          listboxRef = el;
        }}
        style={{
          height: props.height,
          width: "100%",
          overflow: "auto",
          "overflow-y": "auto",
        }}
        scrollToItem={(key) => {
          const idx = comboboxItems().findIndex(
            (option) => option.rawValue.value === key,
          );
          virtualizer().scrollToIndex(idx);
        }}
        class={styles.listbox}
      >
        {(items) => {
          // Update the virtualizer with the filtered items
          const arr = Array.from(items());
          setComboboxItems(arr);

          return (
            <Switch>
              <Match when={props.loading}>
                {props.loadingComponent ?? (
                  <div class="flex w-full justify-center py-2">
                    <Loader />
                  </div>
                )}
              </Match>
              <Match when={!props.loading}>
                <div
                  style={{
                    height: `${virtualizer().getTotalSize()}px`,
                    width: "100%",
                    position: "relative",
                  }}
                >
                  <For each={virtualizer().getVirtualItems()}>
                    {(virtualRow) => {
                      const item: CollectionNode<T> | undefined =
                        items().getItem(virtualRow.key as string);

                      if (!item) {
                        console.warn("Item not found for key:", virtualRow.key);
                        return null;
                      }
                      const isSelected = () =>
                        props.values.some(
                          (v) => v.value === item.rawValue.value,
                        );
                      return (
                        <Combobox.Item
                          item={item}
                          class={cx(
                            styles.searchItem,
                            props.divider && styles.hasDivider,
                          )}
                          style={{
                            position: "absolute",
                            top: 0,
                            left: 0,
                            width: "100%",
                            height: `${virtualRow.size}px`,
                            transform: `translateY(${virtualRow.start}px)`,
                          }}
                        >
                          {props.renderItem(item.rawValue, {
                            selected: isSelected(),
                            disabled: item.disabled,
                          })}
                        </Combobox.Item>
                      );
                    }}
                  </For>
                </div>
              </Match>
            </Switch>
          );
        }}
      </Combobox.Listbox>
      {/* </Combobox.Content> */}
    </Combobox>
  );
}
