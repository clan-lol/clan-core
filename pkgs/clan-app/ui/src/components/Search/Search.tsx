import Icon from "../Icon/Icon";
import { Button } from "../Button/Button";
import styles from "./Search.module.css";
import { Combobox } from "@kobalte/core/combobox";
import { createMemo, createSignal, For, JSX, Match, Switch } from "solid-js";
import { createVirtualizer } from "@tanstack/solid-virtual";
import { CollectionNode } from "@kobalte/core";
import { Loader } from "../Loader/Loader";
import cx from "classnames";

interface Option {
  value: string;
  label: string;
  disabled?: boolean;
}

interface SearchProps<T> {
  onChange: (value: T | null) => void;
  options: T[];
  renderItem: (item: T, opts: { disabled: boolean }) => JSX.Element;
  loading?: boolean;
  loadingComponent?: JSX.Element;
  headerClass?: string;
  height: string; // e.g. '14.5rem'
  divider?: boolean;
}

export function Search<T extends Option>(props: SearchProps<T>) {
  // Controlled input value, to allow resetting the input itself
  const [value, setValue] = createSignal<T | null>(null);
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
      gap: 6,
      overscan: 5,
    });

    return newVirtualizer;
  });

  return (
    <Combobox<T>
      value={value()}
      onChange={(value) => {
        setValue(() => value);
        setInputValue(value ? value.label : "");
        props.onChange(value);
      }}
      class={cx(styles.searchContainer, props.divider && styles.hasDivider)}
      placement="bottom-start"
      options={props.options}
      optionValue="value"
      optionTextValue="label"
      optionLabel="label"
      placeholder="Search a service"
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
          <div class={styles.inputContainer}>
            <Icon icon="Search" color="quaternary" />
            <Combobox.Input
              ref={(el) => {
                inputEl = el;
              }}
              class={styles.searchInput}
              placeholder={"Search a service"}
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
        class={styles.listbox}
        scrollToItem={(key) => {
          const idx = comboboxItems().findIndex(
            (option) => option.rawValue.value === key,
          );
          virtualizer().scrollToIndex(idx);
        }}
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
                      return (
                        <Combobox.Item
                          item={item}
                          class={styles.searchItem}
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
    </Combobox>
  );
}
