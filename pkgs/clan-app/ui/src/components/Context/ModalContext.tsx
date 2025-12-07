import { createModalStore, Modal, ModalMethods } from "@/src/models/modal";
import { createContext, FlowComponent, useContext } from "solid-js";

const ModalContext = createContext<readonly [Modal, ModalMethods]>();

export function useModalContext<T extends string>(): readonly [
  Extract<Modal, { type: T }>,
  ModalMethods,
] {
  const value = useContext(ModalContext) as readonly [
    Extract<Modal, { type: T }>,
    ModalMethods,
  ];
  if (!value) {
    throw new Error(
      "useModalContext must be used within a ModalContextProvider",
    );
  }
  return value;
}

export const ModalContextProvider: FlowComponent = (props) => {
  return (
    <ModalContext.Provider value={createModalStore()}>
      {props.children}
    </ModalContext.Provider>
  );
};
