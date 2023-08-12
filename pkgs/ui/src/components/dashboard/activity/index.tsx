import { DashboardCard } from "@/components/card";
import { NoDataOverlay } from "@/components/noDataOverlay";

export const RecentActivity = () => {
  return (
    <DashboardCard title="Recent Activity">
      <div className="flex h-full w-full justify-center align-middle">
        <NoDataOverlay label="No Activity yet" />
      </div>
    </DashboardCard>
  );
};
