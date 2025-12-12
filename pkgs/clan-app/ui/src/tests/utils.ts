import { Accessor } from "solid-js";
import {
  ClansEntity,
  Clan,
  ClanMethods,
  Clans,
  ClansMethods,
  Machines,
  MachinesMethods,
} from "../models";
import { createClanStore } from "../models/clan/clan";
import { createClansStore } from "../models/clan/clans";
import { MachineEntity } from "../models/machine/machine";
import { createMachinesStore } from "../models/machine/machines";

export function createClansStoreFixture(
  entity: ClansEntity,
): readonly [
  readonly [Accessor<Clan>, ClanMethods],
  readonly [Clans, ClansMethods],
] {
  const [clans, clansMethods] = createClansStore(() => entity);
  const [clan, clanMethods] = createClanStore(
    () => clans.activeClan!,
    [clans, clansMethods],
  );
  return [
    [clan, clanMethods],
    [clans, clansMethods],
  ];
}

export function createMachinesStoreFixture(
  entity: Record<string, MachineEntity>,
): readonly [
  readonly [Accessor<Machines>, MachinesMethods],
  readonly [Accessor<Clan>, ClanMethods],
  readonly [Clans, ClansMethods],
] {
  const [clans, clansMethods] = createClansStore(
    (): ClansEntity => ({
      all: [
        {
          id: "/clan",
          data: {
            name: "testclan",
          },
          dataSchema: {},
          machines: entity,
          services: [],
          globalTags: {
            regular: [],
            special: [],
          },
        },
      ],
      activeIndex: 0,
    }),
  );
  const [clan, clanMethods] = createClanStore(
    () => clans.activeClan!,
    [clans, clansMethods],
  );
  const [machines, machinesMethods] = createMachinesStore(
    () => clans.activeClan!.machines,
    [clan, clanMethods],
    [clans, clansMethods],
  );
  return [
    [machines, machinesMethods],
    [clan, clanMethods],
    [clans, clansMethods],
  ];
}
