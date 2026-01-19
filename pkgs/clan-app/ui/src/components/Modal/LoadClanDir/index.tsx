import { Component, createSignal, onMount } from "solid-js";
import { TextInput } from "@/components/Form/TextInput";
import { Button } from "@/components/Button/Button";
import { Alert } from "@/components/Alert/Alert";
import TitledModal from "../components/TitledModal";
import { useClansContext, useUIContext } from "@/models";

const LoadClanDir: Component = () => {
  const [, { closeModal }] = useUIContext();
  const [, { loadClan, isValidClanDir }] = useClansContext();
  const [clanDir, setClanDir] = createSignal("");
  const [error, setError] = createSignal("");
  const [loading, setLoading] = createSignal(false);
  let inputRef: HTMLInputElement;

  // Focus the input after the modal is mounted to avoid conflicts with dialog focus management
  onMount(() => {
    inputRef.focus();
  });

  const handleSubmit = async (ev: Event) => {
    ev.preventDefault();
    const path = clanDir().trim();

    if (!path) {
      setError("Please enter a path");
      return;
    }

    setLoading(true);
    setError("");

    let isValid;
    try {
      // FIXME: it shouldn't be necessary to check the dir
      // loading the clan should throw the same error
      isValid = await isValidClanDir(path);
      if (!isValid) {
        setError("The specified path is not a valid clan directory");
      }
      await loadClan(path);
      closeModal();
    } catch (err) {
      setError(String(err));
      return;
    } finally {
      setLoading(false);
    }
  };

  return (
    <TitledModal title="Select existing Clan">
      <form onSubmit={handleSubmit} class="flex flex-col gap-4 bg-white p-4">
        {error() && (
          <Alert type="error" icon="info" title="Error" description={error()} />
        )}

        <TextInput
          label="Clan Directory Path"
          description="Enter the full path to your existing clan directory"
          required
          value={clanDir()}
          onChange={setClanDir}
          input={{
            placeholder: "/path/to/your/clan",
            ref: (el: HTMLInputElement) => (inputRef = el),
          }}
        />

        <div
          style={{
            display: "flex",
            gap: "0.5rem",
            "justify-content": "flex-end",
          }}
        >
          <Button
            hierarchy="secondary"
            onClick={() => closeModal()}
            disabled={loading()}
          >
            Cancel
          </Button>
          <Button type="submit" hierarchy="primary" loading={loading()}>
            Select
          </Button>
        </div>
      </form>
    </TitledModal>
  );
};
export default LoadClanDir;
