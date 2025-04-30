import { JSX } from "solid-js";

import { Typography } from "@/src/components/Typography";

type FieldsetProps = {
  legend?: string;
  children: JSX.Element;
  class?: string;
};

export default function Fieldset(props: FieldsetProps) {
  return (
    <fieldset class="flex flex-col gap-y-2.5">
      {props.legend && (
        <div class="px-2">
          <Typography
            hierarchy="body"
            tag="p"
            size="s"
            color="primary"
            weight="medium"
          >
            {props.legend}
          </Typography>
        </div>
      )}
      <div class="flex flex-col gap-y-3 p-5 border border-secondary-200 bg-secondary-50 rounded-md">
        {props.children}
      </div>
    </fieldset>
  );
}
