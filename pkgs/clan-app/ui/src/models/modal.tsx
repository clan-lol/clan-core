// TODO: this is a temporary design
// Modal needs its own overhaul where each Modal component should export
// its own openModal and closeModal with correct typing
import { createStore, SetStoreFunction } from "solid-js/store";
import { Machine } from "./machine";
import { createContext, FlowComponent, useContext } from "solid-js";

const closedModal = { type: null } as { type: null };

export class ModalCancelError extends Error {
  modalType: ModelType;
  constructor(modalType: ModelType) {
    super(`Modal ${modalType} was cancelled`);
    this.modalType = modalType;
  }
}

export type ModalMethods<T extends ModelType> = {
  openModal(...args: OpenModalArgs<T>): Promise<CloseData<T>>;
  closeModal(...args: CloseModalArgs<T>): void;
  cancelModal(): void;
  onCloseModal(callback: (v: CloseData<T>) => void): void;
  onCancelModal(callback: (v: ModalCancelError) => void): void;
};
function modalMethods<T extends ModelType>([modal, setModal]: readonly [
  Modal<T> | typeof closedModal,
  SetStoreFunction<Modal<T> | typeof closedModal>,
]): ModalMethods<T> {
  let promise: Promise<CloseData<T>>;
  let resolve: (data: CloseData<T> | undefined) => void;
  let reject: (err: ModalCancelError) => void;
  const self: ModalMethods<T> = {
    async openModal(...args) {
      const type = args[0];
      if (modal.type) {
        throw new Error(
          `Can not open modal ${type}, there is already an open modal ${modal.type}`,
        );
      }
      if (args.length === 1) {
        setModal(() => ({ type: args[0] }));
      } else {
        setModal(() => ({ type: args[0], data: args[1] }));
      }
      ({ promise, resolve, reject } = Promise.withResolvers<
        CloseData<T> | undefined
      >());
      return await promise;
    },
    closeModal(...args) {
      setModal(() => closedModal);
      resolve(args?.[0]);
    },
    cancelModal() {
      setModal(() => closedModal);
      reject(new ModalCancelError(modal.type!));
    },
    onCloseModal(cb) {
      promise = promise.then((v) => {
        cb(v);
        return v;
      });
    },
    onCancelModal(cb) {
      promise = promise.catch((v) => {
        cb(v);
        return v;
      });
    },
  };
  return self;
}

const ModalContext =
  createContext<
    readonly [Modal<ModelType> | typeof closedModal, ModalMethods<ModelType>]
  >();

export function useModalContext<T extends ModelType>(): readonly [
  Modal<T> | typeof closedModal,
  ModalMethods<T>,
] {
  const value = useContext(ModalContext) as
    | readonly [Modal<T> | typeof closedModal, ModalMethods<T>]
    | undefined;
  if (!value) {
    throw new Error(
      "useModalContext must be used within a ModalContextProvider",
    );
  }
  return value;
}

function createModalStore(): readonly [
  Modal<ModelType> | typeof closedModal,
  ModalMethods<ModelType>,
] {
  const [modal, setModal] = createStore<Modal<ModelType> | typeof closedModal>(
    closedModal,
  );
  return [modal, modalMethods([modal, setModal])];
}

export const ModalContextProvider: FlowComponent = (props) => {
  return (
    <ModalContext.Provider value={createModalStore()}>
      {props.children}
    </ModalContext.Provider>
  );
};

type Union =
  | {
      type: "addMachine";
      openData: {
        position: readonly [number, number];
      };
      closeData: Machine;
    }
  | {
      type: "installMachine";
    };

export type ModelType = Union["type"];
type Modal<T extends ModelType> = "openData" extends keyof Member<T>
  ? { type: T; data: Member<T>["openData"] }
  : { type: T };
export type OpenModalArgs<T extends ModelType> =
  "openData" extends keyof Member<T>
    ? [type: T, data: Member<T>["openData"]]
    : [type: T];
type CloseModalArgs<T extends ModelType> = "closeData" extends keyof Member<T>
  ? undefined extends Member<T>["closeData"]
    ? [data?: CloseData<T>]
    : [data: CloseData<T>]
  : [];
type CloseData<T extends ModelType> = "closeData" extends keyof Member<T>
  ? Member<T>["closeData"]
  : undefined;

type Member<T extends ModelType> = Extract<Union, { type: T }>;
