import { useFlakeHistoryList } from "@/api/flake/flake";
import DynamicFeedIcon from "@mui/icons-material/DynamicFeed";
import MenuIcon from "@mui/icons-material/Menu";
import { Button, Divider, LinearProgress } from "@mui/material";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import * as React from "react";

interface ToolbarButtonProps {
  icon: React.ReactNode;
  onClick: (event: React.MouseEvent<HTMLButtonElement>) => void;
}
export function ToolbarButton(props: ToolbarButtonProps) {
  const { icon, onClick } = props;
  return (
    <Button
      sx={{
        "& .MuiButton-startIcon": {
          m: 0,
        },
      }}
      onClick={onClick}
      startIcon={icon}
      variant="text"
      color="inherit"
      // fullWidth
    />
  );
}

const ClanHistoryMenu = () => {
  const { data, isLoading } = useFlakeHistoryList();

  return (
    <>
      {isLoading ? (
        <LinearProgress />
      ) : (
        data?.data.map((item, index) => <MenuItem key={index}>{item}</MenuItem>)
      )}
      {!isLoading && data?.data.length === 0 && (
        <MenuItem>No Clan History</MenuItem>
      )}
    </>
  );
};

type ToolbarItem = {
  icon: React.ReactNode;
  menu: React.ReactNode;
};
const toolbarItems: ToolbarItem[] = [
  {
    icon: <DynamicFeedIcon />,
    menu: <ClanHistoryMenu />,
  },
];

interface ClanToolbarProps {
  isSidebarVisible: boolean;
  handleSidebar: React.Dispatch<React.SetStateAction<boolean>>;
}
export function ClanToolbar(props: ClanToolbarProps) {
  const { isSidebarVisible, handleSidebar } = props;

  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const [openIdx, setOpenIdx] = React.useState<number | null>(null);

  const handleClick = (
    event: React.MouseEvent<HTMLButtonElement>,
    idx: number
  ) => {
    setAnchorEl(event.currentTarget);
    setOpenIdx(idx);
  };
  const handleClose = () => {
    setAnchorEl(null);
    setOpenIdx(null);
  };
  return (
    <div
      className="flex border-x-0 border-b
    border-t-0 border-solid border-neutral-80"
    >
      {!isSidebarVisible && (
        <ToolbarButton
          icon={<MenuIcon />}
          onClick={() => handleSidebar((c) => !c)}
        />
      )}
      <div
        className="
    grid w-full auto-cols-min grid-flow-col grid-rows-1 
   justify-end gap-0
    "
      >
        {toolbarItems.map((item, index) => (
          <React.Fragment key={index}>
            <Divider flexItem orientation="vertical" />
            <ToolbarButton
              icon={item.icon}
              onClick={(ev) => handleClick(ev, index)}
            />

            <Menu
              id="basic-menu"
              anchorEl={anchorEl}
              open={index == openIdx}
              onClose={handleClose}
              MenuListProps={{
                "aria-labelledby": "basic-button",
              }}
            >
              {item.menu}
            </Menu>
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}
