export * from "./ui";
export * from "./clan";
export * from "./machine";
export * from "./service";

export type DataSchema = Record<
  string,
  { readonly: boolean; reason: string | null; readonly_members: string[] }
>;
