import { Accessor } from "solid-js";
import { Clan, Service } from "..";
import { ServiceOutput, createServiceFromOutput } from "./service";
import { mapObjectValues } from "@/util";

export type Services = {
  all: Record<string, Service>;
  sorted: Service[];
};

export function createServicesFromOutputs(
  outputs: Record<string, ServiceOutput>,
  clan: Accessor<Clan>,
): Services {
  const self: Services = {
    all: mapObjectValues(outputs, ([id, output]) =>
      createServiceFromOutput(id, output, clan),
    ),
    get sorted() {
      return Object.values(this.all).sort((a, b) => {
        return a.id.localeCompare(b.id);
      });
    },
  };
  return self;
}
