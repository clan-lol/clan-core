import { produce, SetStoreFunction } from "solid-js/store";
import { MachinePosition, UI } from "..";

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
    };

export type ModalMethods = {
  showModal(modal: Modal): void;
  closeModal(): void;
};

export function createModalMethods(
  ui: UI,
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
