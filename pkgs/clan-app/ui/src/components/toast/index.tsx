import { toast, Toast } from "solid-toast"; // Make sure to import Toast type
import { Component, JSX, createSignal, onCleanup } from "solid-js";

// --- Icon Components ---

const ErrorIcon: Component = () => (
  <svg
    width="20"
    height="20"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    style={{ "margin-right": "10px", "flex-shrink": "0" }}
  >
    <circle cx="12" cy="12" r="10" fill="#FF4D4F" />
    <path
      d="M12 7V13"
      stroke="white"
      stroke-width="2.5"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    <circle cx="12" cy="16.5" r="1.5" fill="white" />
  </svg>
);

const InfoIcon: Component = () => (
  <svg
    width="20"
    height="20"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    style={{ "margin-right": "10px", "flex-shrink": "0" }}
  >
    <circle cx="12" cy="12" r="10" fill="#2196F3" />
    <path
      d="M12 11V17"
      stroke="white"
      stroke-width="2.5"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    <circle cx="12" cy="8.5" r="1.5" fill="white" />
  </svg>
);

const WarningIcon: Component = () => (
  <svg
    width="20"
    height="20"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    style={{ "margin-right": "10px", "flex-shrink": "0" }}
  >
    <path d="M12 2L22 21H2L12 2Z" fill="#FFC107" />
    <path
      d="M12 9V14"
      stroke="#424242"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    <circle cx="12" cy="16.5" r="1" fill="#424242" />
  </svg>
);

// --- Base Props and Styles ---

export interface BaseToastProps {
  t: Toast;
  message: string;
  onCancel?: () => void; // Optional custom function on X click
}

const baseToastStyle: JSX.CSSProperties = {
  display: "flex",
  "align-items": "center",
  "justify-content": "space-between", // To push X to the right
  gap: "10px", // Space between content and close button
  background: "#FFFFFF",
  color: "#333333",
  padding: "12px 16px",
  "border-radius": "6px",
  "box-shadow": "0 2px 8px rgba(0, 0, 0, 0.12)",
  "font-family":
    'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
  "font-size": "14px",
  "line-height": "1.4",
  "min-width": "280px",
  "max-width": "450px",
};

const closeButtonStyle: JSX.CSSProperties = {
  background: "none",
  border: "none",
  color: "red", // As per original example's X button
  "font-size": "1.5em",
  "font-weight": "bold",
  cursor: "pointer",
  padding: "0 0 0 10px", // Space to its left
  "line-height": "1",
  "align-self": "center", // Ensure vertical alignment
};

// --- Toast Component Definitions ---

// Error Toast
export const ErrorToastComponent: Component<BaseToastProps> = (props) => {
  // Local state for click feedback and exit animation
  let timeoutId: number | undefined;
  const [clicked, setClicked] = createSignal(false);
  const [exiting, setExiting] = createSignal(false);

  const handleToastClick = () => {
    setClicked(true);
    setTimeout(() => {
      setExiting(true);
      timeoutId = window.setTimeout(() => {
        toast.dismiss(props.t.id);
      }, 300); // Match exit animation duration
    }, 100); // Brief color feedback before animating out
  };

  // Cleanup timeout if unmounted early
  onCleanup(() => {
    if (timeoutId) clearTimeout(timeoutId);
  });

  return (
    <div
      style={{
        ...baseToastStyle,
        cursor: "pointer",
        transition: "background 0.15s, opacity 0.3s, transform 0.3s",
        background: clicked()
          ? "#ffeaea"
          : exiting()
            ? "#fff"
            : baseToastStyle.background,
        opacity: exiting() ? 0 : 1,
        transform: exiting() ? "translateY(-20px)" : "none",
      }}
      onClick={handleToastClick}
    >
      <div
        style={{ display: "flex", "align-items": "center", "flex-grow": "1" }}
      >
        <ErrorIcon />
        <span>{props.message}</span>
      </div>
    </div>
  );
};
// Info Toast
export const CancelToastComponent: Component<BaseToastProps> = (props) => {
  let timeoutId: number | undefined;
  const [clicked, setClicked] = createSignal(false);
  const [exiting, setExiting] = createSignal(false);

  // Cleanup timeout if unmounted early
  onCleanup(() => {
    if (timeoutId) clearTimeout(timeoutId);
  });

  const handleButtonClick = (e: MouseEvent) => {
    e.stopPropagation();
    if (props.onCancel) props.onCancel();
    toast.dismiss(props.t.id);
  };

  return (
    <div
      style={{
        ...baseToastStyle,
        cursor: "pointer",
        transition: "background 0.15s, opacity 0.3s, transform 0.3s",
        background: clicked()
          ? "#eaf4ff"
          : exiting()
            ? "#fff"
            : baseToastStyle.background,
        opacity: exiting() ? 0 : 1,
        transform: exiting() ? "translateY(-20px)" : "none",
      }}
    >
      <div
        style={{ display: "flex", "align-items": "center", "flex-grow": "1" }}
      >
        <InfoIcon />
        <span>{props.message}</span>
      </div>
      <button
        onClick={(e) => {
          setClicked(true);
          handleButtonClick(e);
        }}
        style={{
          ...closeButtonStyle,
          color: "#2196F3",
          "font-size": "1em",
          "font-weight": "normal",
          padding: "4px 12px",
          border: "1px solid #2196F3",
          "border-radius": "4px",
          background: clicked() ? "#bbdefb" : "#eaf4ff",
          cursor: "pointer",
          transition: "background 0.15s",
          display: "flex",
          "align-items": "center",
          "justify-content": "center",
          width: "70px",
          height: "32px",
        }}
        aria-label="Cancel"
        disabled={clicked()}
      >
        {clicked() ? (
          // Simple spinner SVG
          <svg
            width="18"
            height="18"
            viewBox="0 0 50 50"
            style={{ display: "block" }}
          >
            <circle
              cx="25"
              cy="25"
              r="20"
              fill="none"
              stroke="#2196F3"
              stroke-width="4"
              stroke-linecap="round"
              stroke-dasharray="31.415, 31.415"
              transform="rotate(72 25 25)"
            >
              <animateTransform
                attributeName="transform"
                type="rotate"
                from="0 25 25"
                to="360 25 25"
                dur="0.8s"
                repeatCount="indefinite"
              />
            </circle>
          </svg>
        ) : (
          "Cancel"
        )}
      </button>
    </div>
  );
};

// Warning Toast
export const WarningToastComponent: Component<BaseToastProps> = (props) => {
  let timeoutId: number | undefined;
  const [clicked, setClicked] = createSignal(false);
  const [exiting, setExiting] = createSignal(false);

  const handleToastClick = () => {
    setClicked(true);
    setTimeout(() => {
      setExiting(true);
      timeoutId = window.setTimeout(() => {
        toast.dismiss(props.t.id);
      }, 300);
    }, 100);
  };

  // Cleanup timeout if unmounted early
  onCleanup(() => {
    if (timeoutId) clearTimeout(timeoutId);
  });

  return (
    <div
      style={{
        ...baseToastStyle,
        cursor: "pointer",
        transition: "background 0.15s, opacity 0.3s, transform 0.3s",
        background: clicked()
          ? "#fff8e1"
          : exiting()
            ? "#fff"
            : baseToastStyle.background,
        opacity: exiting() ? 0 : 1,
        transform: exiting() ? "translateY(-20px)" : "none",
      }}
      onClick={handleToastClick}
    >
      <div
        style={{ display: "flex", "align-items": "center", "flex-grow": "1" }}
      >
        <WarningIcon />
        <span>{props.message}</span>
      </div>
    </div>
  );
};
