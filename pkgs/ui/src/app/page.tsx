"use client";
import { RecentActivity } from "@/components/dashboard/activity";
import { AppOverview } from "@/components/dashboard/appOverview";
import { NetworkOverview } from "@/components/dashboard/NetworkOverview";
import { Notifications } from "@/components/dashboard/notifications";
import { QuickActions } from "@/components/dashboard/quickActions";
import { TaskQueue } from "@/components/dashboard/taskQueue";
import { useAppState } from "@/components/hooks/useAppContext";
import { MachineContextProvider } from "@/components/hooks/useMachines";
import { LoadingOverlay } from "@/components/join/loadingOverlay";
import { tw } from "@/utils/tailwind";
import JoinPrequel from "@/views/joinPrequel";

interface DashboardCardProps {
  children?: React.ReactNode;
  rowSpan?: number;
  sx?: string;
}
const DashboardCard = (props: DashboardCardProps) => {
  const { children, rowSpan, sx = "" } = props;
  return (
    <div
      className={tw`col-span-full row-span-${rowSpan || 1} xl:col-span-1 ${sx}`}
    >
      {children}
    </div>
  );
};

interface DashboardPanelProps {
  children?: React.ReactNode;
}
const DashboardPanel = (props: DashboardPanelProps) => {
  const { children } = props;
  return (
    <div className="col-span-full row-span-1 xl:col-span-2">{children}</div>
  );
};

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
        <div className="flex h-screen w-full">
          <div className="grid w-full auto-rows-max grid-cols-1 grid-rows-none gap-4 xl:grid-cols-2 2xl:grid-cols-3 ">
            <DashboardCard rowSpan={2}>
              <NetworkOverview />
            </DashboardCard>
            <DashboardCard rowSpan={2}>
              <RecentActivity />
            </DashboardCard>
            <DashboardCard>
              <Notifications />
            </DashboardCard>
            <DashboardCard>
              <QuickActions />
            </DashboardCard>
            <DashboardPanel>
              <AppOverview />
            </DashboardPanel>
            <DashboardCard sx={tw`xl:col-span-full 2xl:col-span-1`}>
              <TaskQueue />
            </DashboardCard>
          </div>
        </div>
      </MachineContextProvider>
    );
  }
}
