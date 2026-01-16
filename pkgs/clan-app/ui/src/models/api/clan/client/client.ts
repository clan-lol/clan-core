import { API } from "./types";

export type Methods = keyof API;
export type Header = {
  logging?: { group_path: string[] };
  op_key?: string;
};
export type Body<Method extends Methods> = API[Method]["arguments"];
export type Response<Method extends Methods> = API[Method]["return"];
export type SuccessResponse<Method extends Methods> = Extract<
  Response<Method>,
  { status: "success" }
>;
