import { Button } from "@/src/components/Button/Button";
import Icon from "@/src/components/icon";

interface MachineActionsBarProps {
  machineName: string;
  onInstall: () => void;
  onUpdate: () => void;
  onCredentials: () => void;
}

export function MachineActionsBar(props: MachineActionsBarProps) {
  return (
    <div class="sticky top-0 flex items-center justify-end gap-2 border-b border-secondary-100 bg-secondary-50 px-4 py-2">
      <div class="flex items-center gap-3">
        <div class="button-group flex flex-shrink-0 min-w-0">
          <Button
            variant="light"
            class="flex-1 min-w-0"
            size="s"
            onClick={props.onInstall}
            endIcon={<Icon size={14} icon="Flash" />}
          >
            Install
          </Button>
          <Button
            variant="light"
            class="flex-1 min-w-0"
            size="s"
            onClick={props.onUpdate}
            endIcon={<Icon size={14} icon="Update" />}
          >
            Update
          </Button>
          <Button
            variant="light"
            class="flex-1 min-w-0"
            size="s"
            onClick={props.onCredentials}
            endIcon={<Icon size={14} icon="Folder" />}
          >
            Vars
          </Button>
        </div>
      </div>
    </div>
  );
}
