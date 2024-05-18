const deserialize = (fn: Function) => (str: string) => {
  try {
    fn(JSON.parse(str));
  } catch (e) {
    alert(`Error parsing JSON: ${e}`);
  }
};

export const PYAPI = {
  list_machines: {
    dispatch: (data: null) =>
      // @ts-ignore
      window.webkit.messageHandlers.gtk.postMessage({
        method: "list_machines",
        data,
      }),
    receive: (fn: (response: string[]) => void) => {
      // @ts-ignore
      window.clan.list_machines = deserialize(fn);
    },
  },
};
