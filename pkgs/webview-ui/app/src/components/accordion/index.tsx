import { createSignal, JSX, Show } from "solid-js";

import Icon from "../icon";
import { Typography } from "../Typography";
import { Button } from "../button";

type AccordionProps = {
  title: string;
  children: JSX.Element;
  class?: string;
  initiallyOpen?: boolean;
};

export default function Accordion(props: AccordionProps) {
  const [isOpen, setIsOpen] = createSignal(props.initiallyOpen ?? false);
  return (
    <div
      class={`accordion flex flex-col gap-y-5 ${props.class ?? ""}`}
      tabindex="0"
    >
      <div
        onClick={() => setIsOpen(!isOpen())}
        class="accordion__title h-5 flex gap-x-0.5 items-center justify-end font-medium cursor-pointer px-1"
      >
        <Show
          when={isOpen()}
          fallback={
            <Button
              endIcon={<Icon size={12} icon={"CaretDown"} />}
              variant="light"
              size="s"
            >
              {props.title}
            </Button>
          }
        >
          <Button
            endIcon={<Icon size={12} icon={"CaretUp"} />}
            variant="dark"
            size="s"
          >
            {props.title}
          </Button>
        </Show>
      </div>
      <Show when={isOpen()}>
        <div class="accordion__body">{props.children}</div>
      </Show>
    </div>
  );
}
