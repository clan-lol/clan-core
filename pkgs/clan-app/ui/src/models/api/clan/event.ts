export type ClanMessage = {
  type: string;
};
export type ClanMessageHandler = (msg: ClanMessage) => void;

const handlerGroups: Record<string, ClanMessageHandler[]> = {};
export const onMessage = {
  addListener(name: string, handler: ClanMessageHandler) {
    let handlers = handlerGroups[name];
    if (!handlers) {
      handlers = handlerGroups[name] = [];
    }
    handlers.push(handler);
  },
  removeListener(name: string, handler: ClanMessageHandler) {
    if (!handlerGroups[name]) {
      return;
    }
    const handlers = handlerGroups[name];
    const i = handlers.indexOf(handler);
    if (i === -1) {
      return;
    }
    handlers.splice(i, 1);
  },
};

window.notifyBus = (msg) => {
  for (const handler of handlerGroups[msg.origin] ?? []) {
    handler({
      ...(msg.data ?? {}),
      type: msg.topic,
    });
  }
};
