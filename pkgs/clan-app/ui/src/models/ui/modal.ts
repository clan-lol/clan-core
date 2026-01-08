import { produce, SetStoreFunction } from "solid-js/store";
import { Machine, MachinePosition, UI } from "..";

export type Modal =
  | {
      type: "AddMachine";
      position: MachinePosition;
    }
  | {
      type: "ClanSettings";
    }
  | {
      type: "ListClans";
    }
  | {
      type: "InstallMachine";
      machine: Machine;
    }
  | {
      type: "UpdateMachine";
      machine: Machine;
    };

export type ModalMethods = {
  showModal(this: void, modal: Modal): void;
  closeModal(this: void): void;
};

export function createModalMethods(
  _: UI,
  setUI: SetStoreFunction<UI>,
): ModalMethods {
  const self: ModalMethods = {
    showModal(modal) {
      setUI(
        produce((ui) => {
          ui.modal = modal;
        }),
      );
    },
    closeModal() {
      setUI("modal", null);
    },
  };
  return self;
}
