import { callApi } from "../api";
import { useClanContext } from "@/src/contexts/clan";

export const registerClan = async () => {
  const { setActiveClanURI, addClanURI } = useClanContext();

  try {
    const loc = await callApi("open_file", {
      file_request: { mode: "select_folder" },
    });
    if (loc.status === "success" && loc.data) {
      const data = loc.data[0];
      addClanURI(data);
      setActiveClanURI(data);
      return data;
    }
  } catch (e) {
    //
  }
};

/**
 * Opens the custom file dialog
 * Returns a native FileList to allow interaction with the native input type="file"
 */
export const selectSshKeys = async (): Promise<FileList> => {
  const dataTransfer = new DataTransfer();

  const response = await callApi("open_file", {
    file_request: {
      title: "Select SSH Key",
      mode: "open_file",
      initial_folder: "~/.ssh",
    },
  });
  if (response.status === "success" && response.data) {
    // Add synthetic files to the DataTransfer object
    // FileList cannot be instantiated directly.
    response.data.forEach((filename) => {
      dataTransfer.items.add(new File([], filename));
    });
  }
  return dataTransfer.files;
};
