"use client";
import { NetworkOverview } from "@/components/dashboard/NetworkOverview";
import { RecentActivity } from "@/components/dashboard/activity";
import { AppOverview } from "@/components/dashboard/appOverview";
import { Notifications } from "@/components/dashboard/notifications";
import { QuickActions } from "@/components/dashboard/quickActions";
import { TaskQueue } from "@/components/dashboard/taskQueue";
import { useAppState } from "@/components/hooks/useAppContext";
import { MachineContextProvider } from "@/components/hooks/useMachines";
import { LoadingOverlay } from "@/components/join/loadingOverlay";
import JoinPrequel from "@/views/joinPrequel";

// interface DashboardCardProps {
//   children?: React.ReactNode;
//   rowSpan?: number;
//   sx?: string;
// }
// const DashboardCard = (props: DashboardCardProps) => {
//   const { children, rowSpan, sx = "" } = props;
//   return (
//     // <div className={tw`col-span-full row-span-${rowSpan} 2xl:col-span-1 ${sx}`}>
//     <div className={tw`row-span-2`}>
//       {children}
//     </div>
//   );
// };

// interface DashboardPanelProps {
//   children?: React.ReactNode;
// }
// const DashboardPanel = (props: DashboardPanelProps) => {
//   const { children } = props;
//   return (
//     <div className="col-span-full row-span-1 2xl:col-span-2">{children}</div>
//   );
// };

export default function Dashboard() {
  const { data, isLoading } = useAppState();
  if (isLoading) {
    return (
      <div className="grid h-full place-items-center">
        <div className="mt-8 w-full max-w-xl">
          <LoadingOverlay
            title="Clan Experience"
            subtitle="Loading"
            variant="circle"
          />
        </div>
      </div>
    );
  }
  if (!data.isJoined) {
    return <JoinPrequel />;
  }
  if (data.isJoined) {
    return (
      <MachineContextProvider>
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
      </MachineContextProvider>
    );
  }
}
