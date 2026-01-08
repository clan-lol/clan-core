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
import { createClanMethods } from "../models/clan/clan";
import { createClansMethods, createClansStore } from "../models/clan/clans";
import { MachineEntity } from "../models/machine/machine";
import { createMachinesMethods } from "../models/machine/machines";

export function createClansStoreFixture(
  entity: ClansEntity,
): readonly [
  readonly [Accessor<Clan>, ClanMethods],
  readonly [Clans, ClansMethods],
] {
  const [clans, setClans] = createClansStore(() => entity);
  const clansMethods = createClansMethods(clans, setClans);
  const clan = () => clans.activeClan!;
  const clanMethods = createClanMethods(clan, [clans, clansMethods]);
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
  const [clans, setClans] = createClansStore(
    (): ClansEntity => ({
      all: [
        {
          id: "/clan",
          data: {
            name: "testclan",
          },
          dataSchema: {},
          machines: entity,
          services: {},
          globalTags: {
            regular: [],
            special: [],
          },
        },
      ],
      activeIndex: 0,
    }),
  );
  const clansMethods = createClansMethods(clans, setClans);
  const clan = () => clans.activeClan!;
  const clanMethods = createClanMethods(clan, [clans, clansMethods]);
  const machines = () => clans.activeClan!.machines;
  const machinesMethods = createMachinesMethods(
    machines,
    [clan, clanMethods],
    [clans, clansMethods],
  );
  return [
    [machines, machinesMethods],
    [clan, clanMethods],
    [clans, clansMethods],
  ];
}
