import { customMedia } from "$config";
import { MediaQuery } from "svelte/reactivity";

let mediumMq: MediaQuery | undefined;
let wideMq: MediaQuery | undefined;
export const viewport = {
  get isMedium(): boolean {
    mediumMq ??= new MediaQuery(customMedia.medium);
    return mediumMq.current;
  },
  get isWide(): boolean {
    wideMq ??= new MediaQuery(customMedia.wide);
    return wideMq.current;
  },
};
