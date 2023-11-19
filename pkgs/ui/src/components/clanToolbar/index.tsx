import { useFlakeHistoryList } from "@/api/flake/flake";
import DynamicFeedIcon from "@mui/icons-material/DynamicFeed";
import { IconButton, LinearProgress } from "@mui/material";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import * as React from "react";

interface ToolbarButtonProps {
  icon: React.ReactNode;
  onClick: (event: React.MouseEvent<HTMLButtonElement>) => void;
}
function ToolbarButton(props: ToolbarButtonProps) {
  const { icon, onClick } = props;
  return (
    <div className="">
      <IconButton onClick={onClick}>{icon}</IconButton>
    </div>
  );
}
type ToolbarItem = {
  icon: React.ReactNode;
};
const toolbarItems: ToolbarItem[] = [
  {
    icon: <DynamicFeedIcon />,
  },
];
export function ClanToolbar() {
  const { data, isLoading } = useFlakeHistoryList();
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);
  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };
  const handleClose = () => {
    setAnchorEl(null);
  };
  return (
    <div className="grid w-full auto-cols-min grid-flow-col grid-rows-1 place-items-end justify-end gap-2">
      {toolbarItems.map((item, index) => (
        <ToolbarButton key={index} icon={item.icon} onClick={handleClick} />
      ))}
      <Menu
        id="basic-menu"
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        MenuListProps={{
          "aria-labelledby": "basic-button",
        }}
      >
        {isLoading ? (
          <LinearProgress />
        ) : (
          data?.data.map((item, index) => (
            <MenuItem key={index}>{item}</MenuItem>
          ))
        )}
        {!isLoading && data?.data.length === 0 && (
          <MenuItem>No Clan History</MenuItem>
        )}
      </Menu>
    </div>
  );
}
