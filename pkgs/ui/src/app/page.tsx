interface DashboardCardProps {
  children?: React.ReactNode;
}
const DashboardCard = (props: DashboardCardProps) => {
  const { children } = props;
  return (
    <div className="col-span-full border border-dashed border-slate-400 lg:col-span-1">
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
    <div className="col-span-full border border-dashed border-slate-400 lg:col-span-2">
      {children}
    </div>
  );
};

interface SplitDashboardCardProps {
  children?: React.ReactNode[];
}
const SplitDashboardCard = (props: SplitDashboardCardProps) => {
  const { children } = props;
  return (
    <div className="col-span-full lg:col-span-1">
      <div className="grid h-full grid-cols-1 gap-4">
        {children?.map((row, idx) => (
          <div
            key={idx}
            className="col-span-full border border-dashed border-slate-400"
          >
            {row}
          </div>
        ))}
      </div>
    </div>
  );
};

export default function Dashboard() {
  return (
    <div className="flex h-screen w-full">
      <div className="grid w-full grid-cols-3 gap-4">
        <DashboardCard>Current CLAN Overview</DashboardCard>
        <DashboardCard>Recent Activity Log</DashboardCard>
        <SplitDashboardCard>
          <div>Notifications</div>
          <div>Quick Action</div>
        </SplitDashboardCard>
        <DashboardPanel>Panel</DashboardPanel>
        <DashboardCard>Side Bar (misc)</DashboardCard>
      </div>
    </div>
  );
}
