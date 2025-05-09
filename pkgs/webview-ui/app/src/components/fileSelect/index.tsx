import { FileInput, type FileInputProps } from "@/src/components/FileInput"; // Assuming FileInput can take a ref and has onClick
import { Typography } from "@/src/components/Typography";
import Fieldset from "@/src/Form/fieldset";
import Icon from "@/src/components/icon"; // For displaying file icons
import { callApi } from "@/src/api";
import type {
  FieldComponent,
  FieldValues,
  FieldName,
} from "@modular-forms/solid";
import { Show, For, type Component, type JSX } from "solid-js";

// Types for the file dialog options passed to callApi
interface FileRequestFilter {
  patterns: string[];
  mime_types?: string[];
}

export interface FileDialogOptions {
  title: string;
  filters?: FileRequestFilter;
  initial_folder?: string;
}

// Props for the CustomFileField component
interface FileSelectorOpts<
  TForm extends FieldValues,
  TFieldName extends FieldName<TForm>,
> {
  Field: FieldComponent<TForm>; // The Field component from createForm
  name: TFieldName; // Name of the form field (e.g., "sshKeys", "profilePicture")
  label: string; // Legend for Fieldset or main label for the input
  description?: string | JSX.Element; // Optional description text
  multiple?: boolean; // True if multiple files can be selected, false for single file
  fileDialogOptions: FileDialogOptions; // Configuration for the custom file dialog

  // Optional props for styling
  inputClass?: string;
  fileListClass?: string;
  // You can add more specific props like `validate` if you want to pass them to Field
}

export const FileSelectorField: Component<FileSelectorOpts<any, any>> = (
  props,
) => {
  const {
    Field,
    name,
    label,
    description,
    multiple = false,
    fileDialogOptions,
    inputClass,
    fileListClass,
  } = props;

  // Ref to the underlying HTMLInputElement (assuming FileInput forwards refs or is simple)
  let actualInputElement: HTMLInputElement | undefined;

  const openAndSetFiles = async (event: MouseEvent) => {
    event.preventDefault();
    if (!actualInputElement) {
      console.error(
        "CustomFileField: Input element ref is not set. Cannot proceed.",
      );
      return;
    }

    const dataTransfer = new DataTransfer();
    const mode = multiple ? "open_multiple_files" : "open_file";

    try {
      const response = await callApi("open_file", {
        file_request: {
          title: fileDialogOptions.title,
          mode: mode,
          filters: fileDialogOptions.filters,
          initial_folder: fileDialogOptions.initial_folder,
        },
      });

      if (
        response.status === "success" &&
        response.data &&
        Array.isArray(response.data)
      ) {
        (response.data as string[]).forEach((filename) => {
          // Create File objects. Content is empty as we only have paths.
          // Type might be generic or derived if possible.
          dataTransfer.items.add(
            new File([], filename, { type: "application/octet-stream" }),
          );
        });
      } else if (response.status === "error") {
        // Consider using a toast or other user notification for API errors
        console.error("Error from open_file API:", response.errors);
      }
    } catch (error) {
      console.error("Failed to call open_file API:", error);
      // Consider using a toast here
    }

    // Set the FileList on the actual input element
    Object.defineProperty(actualInputElement, "files", {
      value: dataTransfer.files,
      writable: true,
    });

    // Dispatch an 'input' event so modular-forms updates its state
    const inputEvent = new Event("input", { bubbles: true, cancelable: true });
    actualInputElement.dispatchEvent(inputEvent);

    // Optionally, dispatch 'change' if your forms setup relies more on it
    // const changeEvent = new Event("change", { bubbles: true, cancelable: true });
    // actualInputElement.dispatchEvent(changeEvent);
  };

  return (
    <Fieldset legend={label}>
      {description &&
        (typeof description === "string" ? (
          <Typography hierarchy="body" size="s" weight="medium" class="mb-2">
            {description}
          </Typography>
        ) : (
          description
        ))}

      <Field name={name} type={multiple ? "File[]" : "File"}>
        {(field, fieldProps) => (
          <>
            {/* 
              This FileInput component should be clickable.
              Its 'ref' needs to point to the actual <input type="file"> element.
              If FileInput is complex, it might need an 'inputRef' prop or similar.
            */}
            <FileInput
              {...(fieldProps as FileInputProps)} // Spread modular-forms props
              ref={(el: HTMLInputElement) => {
                (fieldProps as any).ref(el); // Pass ref to modular-forms
                actualInputElement = el; // Capture for local use
              }}
              class={inputClass}
              multiple={multiple}
              // The onClick here triggers our custom dialog logic
              onClick={openAndSetFiles}
              // The 'value' prop for a file input is not for displaying selected files directly.
              // We'll display them below. FileInput might show placeholder text.
              // value={undefined} // Explicitly not setting value from field.value here
              error={field.error} // Display error from modular-forms
            />
            {field.error && (
              <Typography color="error" hierarchy="body" size="xs" class="mt-1">
                {field.error}
              </Typography>
            )}

            {/* Display the list of selected files */}
            <Show
              when={
                field.value &&
                (multiple
                  ? (field.value as File[]).length > 0
                  : field.value instanceof File)
              }
            >
              <div class={`mt-2 space-y-1 ${fileListClass || ""}`}>
                <For
                  each={
                    multiple
                      ? (field.value as File[])
                      : field.value instanceof File
                        ? [field.value as File]
                        : []
                  }
                >
                  {(file) => (
                    <div class="flex items-center justify-between rounded border border-def-1 bg-bg-2 p-2 text-sm">
                      <span class="truncate" title={file.name}>
                        <Icon icon="File" class="mr-2 inline-block" size={14} />
                        {file.name}
                      </span>
                      {/* A remove button per file is complex with FileList & modular-forms.
                          For now, clearing all files is simpler (e.g., via FileInput's own clear).
                          Or, the user re-selects files to change the selection. */}
                    </div>
                  )}
                </For>
              </div>
            </Show>
          </>
        )}
      </Field>
    </Fieldset>
  );
};
