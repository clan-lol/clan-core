import Icon from "../Icon/Icon";
import { Button } from "../Button/Button";
import styles from "./Search.module.css";
import { Combobox } from "@kobalte/core/combobox";
import { createMemo, createSignal, For } from "solid-js";
import { Typography } from "../Typography/Typography";
import { createVirtualizer } from "@tanstack/solid-virtual";
import { CollectionNode } from "@kobalte/core/*";

export interface Module {
  value: string;
  name: string;
  input: string;
  description: string;
}

export interface SearchProps {
  onChange: (value: Module | null) => void;
  options: Module[];
}
export function Search(props: SearchProps) {
  // Controlled input value, to allow resetting the input itself
  const [value, setValue] = createSignal<Module | null>(null);
  const [inputValue, setInputValue] = createSignal<string>("");

  let inputEl: HTMLInputElement;

  let listboxRef: HTMLUListElement;

  // const [currentItems, setItems] = createSignal(ALL_MODULES_OPTIONS_FLAT);
  const [comboboxItems, setComboboxItems] = createSignal<
    CollectionNode<Module>[]
  >(
    props.options.map((item) => ({
      rawValue: item,
    })) as CollectionNode<Module>[],
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
    <Combobox<Module>
      value={value()}
      onChange={(value) => {
        setValue(value);
        setInputValue(value ? value.name : "");
        props.onChange(value);
      }}
      class={styles.searchContainer}
      placement="bottom-start"
      options={props.options}
      optionValue="value"
      optionTextValue="name"
      optionLabel="name"
      placeholder="Search a service"
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
      <Combobox.Control<Module> class={styles.searchHeader}>
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
      <Combobox.Portal>
        <Combobox.Content class={styles.searchContent} tabIndex={-1}>
          <Combobox.Listbox<Module>
            ref={(el) => {
              listboxRef = el;
            }}
            style={{
              height: "100%",
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
          >
            {(items) => {
              // Update the virtualizer with the filtered items
              const arr = Array.from(items());
              setComboboxItems(arr);

              return (
                <div
                  style={{
                    height: `${virtualizer().getTotalSize()}px`,
                    width: "100%",
                    position: "relative",
                  }}
                >
                  <For each={virtualizer().getVirtualItems()}>
                    {(virtualRow) => {
                      const item: CollectionNode<Module> | undefined =
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
                          <div role="complementary">
                            <Icon icon="Code" />
                          </div>
                          <div role="option">
                            <Combobox.ItemLabel class="flex">
                              <Typography
                                hierarchy="body"
                                size="s"
                                weight="medium"
                                inverted
                              >
                                {item.rawValue.name}
                              </Typography>
                            </Combobox.ItemLabel>
                            <Typography
                              hierarchy="body"
                              size="xxs"
                              weight="normal"
                              color="quaternary"
                              inverted
                              class="flex justify-between"
                            >
                              <span>{item.rawValue.description}</span>
                              <span>by {item.rawValue.input}</span>
                            </Typography>
                          </div>
                        </Combobox.Item>
                      );
                    }}
                  </For>
                </div>
              );
            }}
          </Combobox.Listbox>
        </Combobox.Content>
      </Combobox.Portal>
    </Combobox>
  );
}
