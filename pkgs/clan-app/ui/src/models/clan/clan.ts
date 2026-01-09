import { Accessor } from "solid-js";
import api from "../api";
import {
  Clans,
  ClansMethods,
  DataSchema,
  Machines,
  ServiceInstances,
  Services,
} from "..";
import { reconcile, SetStoreFunction } from "solid-js/store";
import { MachineEntity } from "../machine/machine";
import { createMachines } from "../machine/machines";
import { createServices } from "../service/services";
import { ServiceEntity } from "../service/service";
import { createServiceInstances } from "../service/instances";
import { DeepRequired } from "@/src/util";

export type ClanMember = {
  readonly type: "tag" | "machine";
  readonly name: string;
};

export type ClanOutput = {
  readonly id: string;
  readonly data: ClanDataOutput;
  readonly dataSchema: DataSchema;
  readonly machines: Record<string, MachineEntity>;
  readonly services: Record<string, ServiceEntity>;
  readonly globalTags: Tags;
};

export type ClanData = {
  name: string;
  description?: string;
  domain?: string;
};
export type ClanDataOutput = DeepRequired<ClanData>;

export type Clan = Omit<
  ClanOutput,
  "data" | "machines" | "services" | "serviceInstances"
> & {
  readonly clans: Clans;
  readonly machines: Machines;
  readonly services: Services;
  data: ClanDataOutput;
  readonly members: ClanMember[];
  readonly index: number;
  serviceInstances: ServiceInstances;
  readonly isActive: boolean;
};

export type ClanMetaOutput = {
  readonly id: string;
  readonly data: ClanMetaDataOutput;
};
export type ClanMetaDataOutput = {
  readonly name: string;
  readonly description: string;
};
export type ClanMeta = Omit<ClanMetaOutput, "data"> & {
  readonly data: ClanMetaDataOutput;
  readonly clans: Clans;
  readonly index: number;
};

export type Tags = {
  // TODO: rename backend's data.options to data.regular, options is too
  // overloaded a name
  readonly regular: string[];
  readonly special: string[];
};

export type ClanMethods = {
  setClan: SetStoreFunction<Clan>;
  activateClan(this: void): Promise<void>;
  deactivateClan(this: void): void;
  updateClanData(this: void, data: ClanData): Promise<void>;
  removeClan(this: void): void;
  refreshClan(this: void): Promise<void>;
};
export function createClanMethods(
  clan: Accessor<Clan>,
  [clans, { setClans, activateClan, deactivateClan, removeClan }]: readonly [
    Clans,
    ClansMethods,
  ],
): ClanMethods {
  const setClan: SetStoreFunction<Clan> = (...args: unknown[]) => {
    const i = clan().index;
    if (i === -1) {
      throw new Error(
        `This clan does not belong to the known clan: ${clan().id}`,
      );
    }
    // @ts-expect-error ...args won't infer properly for overloaded functions
    setClans("all", i, ...args);
  };
  const self: ClanMethods = {
    setClan,
    async activateClan(this: void) {
      await activateClan(clan());
    },
    deactivateClan(this: void) {
      if (clan().isActive) {
        deactivateClan();
      }
    },
    async updateClanData(this: void, data) {
      // TODO: Use partial update once supported by backend and solidjs
      // https://github.com/solidjs/solid/issues/2475
      const d = { ...clan().data, ...data };
      await api.clan.updateClanData(clan().id, d);
      setClan("data", d);
    },
    removeClan(this: void) {
      removeClan(clan());
    },
    async refreshClan(this: void) {
      const output = await api.clan.getClan(clan().id);
      const newClan = createClanFromOutput(output, clans);
      setClan(reconcile(newClan));
    },
  };
  return self;
}

export function createClanFromOutput(output: ClanOutput, clans: Clans): Clan {
  const { id } = output;
  const clan: Accessor<Clan> = () => {
    const clan = clans.all.find((clan) => clan.id === id);
    if (!clan) {
      throw new Error(`Clan does not exist: ${id}`);
    }
    if (isClan(clan)) return clan;
    throw new Error(`Accessing a clan that has not been activated yet: ${id}`);
  };
  return {
    ...output,
    get clans() {
      return clans;
    },
    machines: createMachines(output.machines, clan),
    services: createServices(output.services, clan),
    serviceInstances: createServiceInstances(output.services, clan),
    get members() {
      return [
        ...Object.keys(this.machines.all).map((name) => ({
          type: "machine" as const,
          name,
        })),
        ...this.globalTags.regular
          .concat(this.globalTags.special)
          .map((name) => ({ type: "tag" as const, name })),
      ].sort((a, b) => a.name.localeCompare(b.name));
    },
    get index() {
      return this.clans.all.indexOf(this);
    },
    get isActive() {
      return clans.activeClan === this;
    },
  };
}
export function createClanMetaFromOutput(
  output: ClanMetaOutput,
  clans: Clans,
): ClanMeta {
  return {
    ...output,
    get clans() {
      return clans;
    },
    get index(): number {
      return this.clans.all.findIndex((clan) => clan.id === this.id);
    },
  };
}

export function isClan(clan: Clan | ClanMeta): clan is Clan {
  return "machines" in clan;
}
