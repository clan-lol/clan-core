import { JSX, Show } from "solid-js";

interface SimpleModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: JSX.Element;
}

export const SimpleModal = (props: SimpleModalProps) => {
  return (
    <Show when={props.open}>
      <div class="fixed inset-0 z-50 flex items-center justify-center">
        {/* Backdrop */}
        <div class="fixed inset-0 bg-black/50" onClick={props.onClose} />

        {/* Modal Content */}
        <div class="relative mx-4 w-full max-w-md rounded-lg bg-white shadow-lg">
          {/* Header */}
          <Show when={props.title}>
            <div class="flex items-center justify-between border-b p-4">
              <h3 class="text-lg font-semibold">{props.title}</h3>
              <button
                type="button"
                class="text-gray-400 hover:text-gray-600"
                onClick={props.onClose}
              >
                ×
              </button>
            </div>
          </Show>

          {/* Body */}
          <div>{props.children}</div>
        </div>
      </div>
    </Show>
  );
};
