import { DashboardCard } from "@/components/card";
import Image from "next/image";
interface AppCardProps {
  name: string;
  icon?: string;
}
const AppCard = (props: AppCardProps) => {
  const { name, icon } = props;
  const iconPath = icon
    ? `/app-icons/${icon}`
    : "app-icons/app-placeholder.svg";
  return (
    <div
      role="button"
      className="flex h-40 w-40  cursor-pointer items-center justify-center rounded-3xl p-2
       align-middle shadow-md ring-2 ring-inset ring-blue-90 
       hover:bg-neutral-90 focus:bg-neutral-90 active:bg-neutral-80 
       dark:hover:bg-neutral-10 dark:focus:bg-neutral-10 dark:active:bg-neutral-20"
    >
      <div className="flex w-full flex-col justify-center">
        <div className="my-1 flex h-[22] w-[22] items-center justify-center self-center overflow-visible p-1 dark:invert">
          <Image
            src={iconPath}
            alt={`${name}-app-icon`}
            width={18 * 3}
            height={18 * 3}
          />
        </div>
        <div className="flex w-full justify-center">{name}</div>
      </div>
    </div>
  );
};

const apps = [
  {
    name: "Firefox",
    icon: "firefox.svg",
  },
  {
    name: "Discord",
    icon: "discord.svg",
  },
  {
    name: "Docs",
  },
  {
    name: "Dochub",
    icon: "dochub.svg",
  },
  {
    name: "Chess",
    icon: "chess.svg",
  },
  {
    name: "Games",
    icon: "games.svg",
  },
  {
    name: "Mail",
    icon: "mail.svg",
  },
  {
    name: "Public transport",
    icon: "public-transport.svg",
  },
  {
    name: "Outlook",
    icon: "mail.svg",
  },
  {
    name: "Youtube",
    icon: "youtube.svg",
  },
];

export const AppOverview = () => {
  return (
    <DashboardCard title="Applications">
      <div className="flex h-full w-full justify-center">
        <div className="flex h-full w-fit justify-center">
          <div className="grid w-full auto-cols-min auto-rows-min  grid-cols-2 gap-8 py-8 sm:grid-cols-3 md:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 ">
            {apps.map((app) => (
              <AppCard key={app.name} name={app.name} icon={app.icon} />
            ))}
          </div>
        </div>
      </div>
    </DashboardCard>
  );
};
