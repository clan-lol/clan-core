export * from "./sys";
export * from "./ui";
export * from "./clan";
export * from "./machine";
export * from "./service";

export type DataSchema = Record<
  string,
  { readonly: boolean; reason: string | null; readonly_members: string[] }
>;

export const config = {
  clanAPIBase: import.meta.env.VITE_CLAN_API_BASE as string,
  get clanAPIType() {
    return this.clanAPIBase ? "http" : "rpc";
  },
};
