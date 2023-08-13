import { DashboardCard } from "@/components/card";

import SyncIcon from "@mui/icons-material/Sync";
import ScheduleIcon from "@mui/icons-material/Schedule";
import DoneIcon from "@mui/icons-material/Done";
import { ReactNode } from "react";
import { Chip } from "@mui/material";

const statusMap = {
  running: <SyncIcon className="animate-bounce" />,
  done: <DoneIcon />,
  planned: <ScheduleIcon />,
};

interface TaskEntryProps {
  status: ReactNode;
  result: "default" | "error" | "info" | "success" | "warning";
  task: string;
  details?: string;
}
const TaskEntry = (props: TaskEntryProps) => {
  const { result, task, details, status } = props;
  return (
    <>
      <div className="col-span-1">{status}</div>
      <div className="col-span-4">{task}</div>
      <div className="col-span-1">
        <Chip color={result} label={result} />
      </div>
    </>
  );
};

export const TaskQueue = () => {
  return (
    <DashboardCard title="Task Queue">
      <div className="grid grid-cols-6 gap-2 p-4">
        <TaskEntry
          result="success"
          task="Update DevX"
          status={statusMap.done}
        />
        <TaskEntry
          result="default"
          task="Update XYZ"
          status={statusMap.running}
        />
        <TaskEntry
          result="default"
          task="Update ABC"
          status={statusMap.planned}
        />
      </div>
    </DashboardCard>
  );
};
