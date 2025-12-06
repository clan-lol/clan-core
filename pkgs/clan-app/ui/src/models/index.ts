export * from "./clan";
export * from "./machine";

export type DataSchema = Record<
  string,
  { readonly: boolean; reason: string | null; readonly_members: string[] }
>;
