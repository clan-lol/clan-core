import {
  MachinesQuery,
  ServiceInstancesQuery,
  ServiceModules,
} from "@/src/hooks/queries";
import { TagType } from "./Service";

export interface ServiceStoreType {
  roles: Record<string, TagType[]>;
  currentRole?: string;
  close: () => void;
  handleSubmit: SubmitServiceHandler;
  action: "create" | "update";
}

// TODO: Ideally we would impot this from a backend model package
interface InventoryInstance {
  name: string;
  module: {
    name: string;
    input?: string | null;
  };
  roles: Record<string, RoleType>;
}

export interface RoleType {
  machines: Record<string, { settings?: unknown }>;
  tags: Record<string, unknown>;
}

export type SubmitServiceHandler = (
  values: InventoryInstance,
  action: "create" | "update",
) => void | Promise<void>;

type ModuleItem = ServiceModules["modules"][number];

export interface Module {
  value: string;
  label: string;
  raw: ModuleItem;
}

type ValueOf<T> = T[keyof T];

export type Instance = ValueOf<NonNullable<ServiceInstancesQuery["data"]>>;

/**
 * Collect all members (machines and tags) for a given role in a service instance
 *
 * TODO: Make this native feature of the API
 *
 */
export function getRoleMembers(
  instance: Instance,
  all_machines: NonNullable<MachinesQuery["data"]>,
  role: string,
) {
  const tags = Object.keys(instance.roles?.[role].tags || {});
  const machines = Object.keys(instance.roles?.[role].machines || {});

  const machineTags = machines.map((m) => ({
    value: "m_" + m,
    label: m,
    type: "machine" as const,
  }));
  const tagsTags = tags.map((t) => {
    return {
      value: "t_" + t,
      label: t,
      type: "tag" as const,
      members: Object.entries(all_machines)
        .filter(([_, m]) => m.data.tags?.includes(t))
        .map(([k]) => k),
    };
  });
  console.log("Members for role", role, [...machineTags, ...tagsTags]);

  const roleMembers = [...machineTags, ...tagsTags].sort((a, b) =>
    a.label.localeCompare(b.label),
  );
  return roleMembers;
}
