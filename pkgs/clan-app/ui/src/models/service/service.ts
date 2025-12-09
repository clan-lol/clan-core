import { Clan, Clans, ClansMethods, ServiceInstance } from "..";
import { ServiceInstanceEntity, toServiceInstance } from "./instance";

export type ServiceEntity = {
  readonly id: string;
  readonly instances: ServiceInstanceEntity[];
};
export type Service = Omit<ServiceEntity, "instances"> & {
  readonly clan: Clan;
  readonly instances: ServiceInstance[];
};

export function toService(
  entity: ServiceEntity,
  clanId: string,
  clansValue: readonly [Clans, ClansMethods],
): Service {
  const [, { existingClan }] = clansValue;
  return {
    ...entity,
    get clan(): Clan {
      return existingClan(clanId);
    },
    instances: entity.instances.map((instance) =>
      toServiceInstance(instance, entity.id, clanId, clansValue),
    ),
  };
}
