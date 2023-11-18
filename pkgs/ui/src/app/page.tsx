import { NetworkOverview } from "@/components/dashboard/NetworkOverview";
import { RecentActivity } from "@/components/dashboard/activity";
import { AppOverview } from "@/components/dashboard/appOverview";
import { Notifications } from "@/components/dashboard/notifications";
import { QuickActions } from "@/components/dashboard/quickActions";
import { TaskQueue } from "@/components/dashboard/taskQueue";

export default function Dashboard() {
  return (
    <div className="flex w-full">
      <div className="grid w-full grid-flow-row grid-cols-3 gap-4">
        <div className="row-span-2">
          <NetworkOverview />
        </div>
        <div className="col-span-2">
          <AppOverview />
        </div>
        <div className="row-span-2">
          <RecentActivity />
        </div>
        <QuickActions />
        <Notifications />
        <TaskQueue />
      </div>
    </div>
  );
}
