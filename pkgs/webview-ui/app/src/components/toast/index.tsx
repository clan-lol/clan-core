import { toast, Toast } from "solid-toast"; // Make sure to import Toast type
import { Component, JSX } from "solid-js";

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
export interface ErrorToastProps extends BaseToastProps {}
export const ErrorToastComponent: Component<ErrorToastProps> = (props) => {
  const handleCancelClick = () => {
    if (props.onCancel) {
      props.onCancel();
    }
    toast.dismiss(props.t.id);
  };

  return (
    <div style={baseToastStyle}>
      <div
        style={{ display: "flex", "align-items": "center", "flex-grow": "1" }}
      >
        <ErrorIcon />
        <span>{props.message}</span>
      </div>
      <button
        onClick={handleCancelClick}
        style={closeButtonStyle}
        aria-label="Close notification"
      >
        ✕
      </button>
    </div>
  );
};

// Info Toast
export interface InfoToastProps extends BaseToastProps {}
export const InfoToastComponent: Component<InfoToastProps> = (props) => {
  const handleCancelClick = () => {
    if (props.onCancel) {
      props.onCancel();
    }
    toast.dismiss(props.t.id);
  };

  return (
    <div style={baseToastStyle}>
      <div
        style={{ display: "flex", "align-items": "center", "flex-grow": "1" }}
      >
        <InfoIcon />
        <span>{props.message}</span>
      </div>
      <button
        onClick={handleCancelClick}
        style={closeButtonStyle}
        aria-label="Close notification"
      >
        ✕
      </button>
    </div>
  );
};

// Warning Toast
export interface WarningToastProps extends BaseToastProps {}
export const WarningToastComponent: Component<WarningToastProps> = (props) => {
  const handleCancelClick = () => {
    if (props.onCancel) {
      props.onCancel();
    }
    toast.dismiss(props.t.id);
  };

  return (
    <div style={baseToastStyle}>
      <div
        style={{ display: "flex", "align-items": "center", "flex-grow": "1" }}
      >
        <WarningIcon />
        <span>{props.message}</span>
      </div>
      <button
        onClick={handleCancelClick}
        style={closeButtonStyle}
        aria-label="Close notification"
      >
        ✕
      </button>
    </div>
  );
};

// --- Example Usage ---
/*
import { toast } from 'solid-toast';
import {
  ErrorToastComponent,
  InfoToastComponent,
  WarningToastComponent
} from './your-toast-components-file'; // Adjust path as necessary

const logCancel = (type: string) => console.log(`${type} toast cancelled by user.`);

// Function to show an error toast
export const showErrorToast = (message: string) => {
  toast.custom((t) => (
    <ErrorToastComponent
      t={t}
      message={message}
      onCancel={() => logCancel('Error')}
    />
  ), { duration: Infinity }); // Use Infinity duration if you want it to only close on X click
};

// Function to show an info toast
export const showInfoToast = (message: string) => {
  toast.custom((t) => (
    <InfoToastComponent
      t={t}
      message={message}
      // onCancel not provided, so only dismisses
    />
  ), { duration: 6000 }); // Or some default duration
};

// Function to show a warning toast
export const showWarningToast = (message: string) => {
  toast.custom((t) => (
    <WarningToastComponent
      t={t}
      message={message}
      onCancel={() => alert('Warning toast was cancelled!')}
    />
  ), { duration: Infinity });
};

// How to use them:
// showErrorToast("Target IP must be provided.");
// showInfoToast("Your profile has been updated successfully.");
// showWarningToast("Your session is about to expire in 5 minutes.");
*/
