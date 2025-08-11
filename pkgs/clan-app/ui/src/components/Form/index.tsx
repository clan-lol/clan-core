import { FieldSchema } from "@/src/hooks/queries";
import { Maybe } from "@modular-forms/solid";

export const tooltipText = <T extends object, K extends keyof T>(
  name: K,
  schema: FieldSchema<T>,
  staticValue: Maybe<string> = undefined,
): Maybe<string> => {
  const entry = schema[name];

  // return the static value if there is no field schema entry, or the entry
  // indicates the field is writeable
  if (!(entry && entry.readonly)) {
    return staticValue;
  }

  const components: string[] = [];

  if (staticValue) {
    components.push(staticValue);
  }

  components.push(`This field is read-only`);
  if (entry.reason) {
    components.push(entry.reason);
  }

  return components.join(". ");
};
