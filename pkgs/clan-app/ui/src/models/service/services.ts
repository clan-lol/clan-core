import { Accessor } from "solid-js";
import { Clan, Service } from "..";
import { ServiceEntity, toService } from "./service";
import { mapObjectValues } from "@/src/util";

export type Services = {
  all: Record<string, Service>;
  sorted: Service[];
};

export function toServices(
  entities: Record<string, ServiceEntity>,
  clan: Accessor<Clan>,
): Services {
  const self: Services = {
    all: mapObjectValues(entities, ([, entity]) => toService(entity, clan)),
    get sorted() {
      return Object.values(this.all).sort((a, b) => {
        return a.id.localeCompare(b.id);
      });
    },
  };
  return self;
}
