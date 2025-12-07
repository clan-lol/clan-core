import { createStore, SetStoreFunction } from "solid-js/store";
import { Machine } from "./machine";

const closedModal = { type: null } as const;

export function createModalStore(): readonly [Modal, ModalMethods] {
  const [modal, setModal] = createStore<Modal>(closedModal);
  return [modal, modalMethods([modal, setModal])];
}

export type ModalMethods = {
  openAddMachineModal(
    data: Extract<Modal, { type: "addMachine" }>["data"],
  ): Promise<Machine | undefined>;
  closeAddMachineModal(machine?: Machine): void;
  onCloseAddMachineModal(
    callback: (machine: Machine | undefined) => void,
  ): void;
};

function modalMethods([modal, setModal]: readonly [
  Modal,
  SetStoreFunction<Modal>,
]): ModalMethods {
  function checkOpenModal(type: string) {
    if (modal.type) {
      throw new Error(
        `Can not open modal ${type}, there is already an open modal ${modal.type}`,
      );
    }
  }
  function checkCloseModal(type: string) {
    if (!modal.type) {
      throw new Error(`Can not close modal ${type}, no modal is open`);
    }
    if (modal.type !== type) {
      throw new Error(
        `Can not close modal ${type}, the current open modal is ${modal.type}`,
      );
    }
  }
  const self: ModalMethods = {
    ...(() => {
      let promise: Promise<Machine | undefined>;
      let resolve: (machine?: Machine) => void;
      const type = "addMachine";
      return {
        async openAddMachineModal(data) {
          checkOpenModal(type);
          setModal({ type, data });
          ({ promise, resolve } = Promise.withResolvers<Machine | undefined>());
          return await promise;
        },
        closeAddMachineModal(machine) {
          checkCloseModal(type);
          setModal(closedModal);
          resolve(machine);
        },
        onCloseAddMachineModal(cb) {
          promise = promise.then((machine) => {
            cb(machine);
            return machine;
          });
        },
      };
    })(),
  };
  return self;
}

export type Modal =
  | {
      type: "addMachine";
      data: {
        position: readonly [number, number];
      };
    }
  | {
      type: "installMachine";
    }
  | typeof closedModal;

export type OpenModal = Exclude<Modal, { type: null }>;
