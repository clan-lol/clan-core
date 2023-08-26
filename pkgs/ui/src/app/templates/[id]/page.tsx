"use client";

import {
  Attachment,
  ChevronLeft,
  Delete,
  Edit,
  Group,
  Key,
  MenuOpen,
  NetworkCell,
  Settings,
  SettingsEthernet,
  VisibilityOff,
} from "@mui/icons-material";
import {
  Avatar,
  Button,
  Divider,
  IconButton,
  List,
  ListItem,
  ListItemAvatar,
  ListItemSecondaryAction,
  ListItemText,
  ListSubheader,
  Menu,
  MenuItem,
  Typography,
} from "@mui/material";
import { useState } from "react";
import { useListMachines } from "@api/default/default";

export async function generateStaticParams() {
  return [{ id: "1" }, { id: "2" }];
}

function getTemplate(params: { id: string }) {
  console.log({ params });
  // const res = await fetch(`https://.../posts/${params.id}`);
  return {
    short: `My Template ${params.id}`,
  };
}

interface TemplateDetailProps {
  params: { id: string };
}
export function TemplateDetail({ params }: TemplateDetailProps) {
  const { data, isLoading } = useListMachines();
  console.log({ data, isLoading });
  const details = getTemplate(params);

  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };
  const handleClose = () => {
    setAnchorEl(null);
  };

  return (
    <div className="flex w-full flex-col items-center justify-center">
      <div className="w-full">
        <Button
          color="secondary"
          LinkComponent={"a"}
          href="/templates"
          startIcon={<ChevronLeft />}
        >
          Back
        </Button>
      </div>
      <div className="h-full w-full border border-solid border-slate-100 bg-slate-50 shadow-sm shadow-slate-400">
        <div className="flex w-full flex-col items-center justify-center xl:p-2">
          <Avatar className="m-1 h-20 w-20 bg-violet-600">
            <Typography variant="h5">N</Typography>
          </Avatar>
          <Typography variant="h6" className="text-violet-600">
            {details.short}
          </Typography>
          <div className="w-full">
            <List
              className="xl:px-4"
              sx={{
                ".MuiListSubheader-root": {
                  px: 0,
                },
                ".MuiListItem-root": {
                  px: 0,
                },
              }}
            >
              <ListSubheader>
                <Typography variant="caption">Details</Typography>
              </ListSubheader>
              <ListItem>
                <ListItemAvatar>
                  <SettingsEthernet />
                </ListItemAvatar>
                <ListItemText primary="network" secondary="10.9.20.2" />
              </ListItem>
              <ListItem>
                <ListItemAvatar>
                  <Key />
                </ListItemAvatar>
                <ListItemText primary="secrets" secondary={"< ...hidden >"} />
              </ListItem>
              <ListItem>
                <ListItemAvatar>
                  <Group />
                </ListItemAvatar>
                <ListItemText primary="clans" secondary={"Boss clan.lol"} />
              </ListItem>
              <ListItem>
                <ListItemAvatar>
                  <Attachment />
                </ListItemAvatar>
                <ListItemText
                  primary="Image"
                  secondary={"/nix/store/12789-image-clan-lol"}
                />
                <ListItemSecondaryAction>
                  <IconButton onClick={handleClick}>
                    <Settings />
                  </IconButton>
                  <Menu
                    MenuListProps={{
                      className: "m-2",
                    }}
                    id="image-menu"
                    aria-labelledby="image-menu"
                    anchorEl={anchorEl}
                    open={open}
                    onClose={handleClose}
                    anchorOrigin={{
                      vertical: "top",
                      horizontal: "left",
                    }}
                    transformOrigin={{
                      vertical: "top",
                      horizontal: "left",
                    }}
                  >
                    <MenuItem>View</MenuItem>
                    <MenuItem>Rebuild</MenuItem>
                    <MenuItem>Delete</MenuItem>
                  </Menu>
                </ListItemSecondaryAction>
              </ListItem>
              <ListItem>
                <ListItemAvatar>
                  <Group />
                </ListItemAvatar>
                <ListItemText
                  primary="nodes"
                  secondary={"Dad's PC; Mum; Olaf; ... 3 more"}
                />
              </ListItem>
            </List>
          </div>
        </div>
        <div className="mt-2 flex w-full justify-evenly">
          <Button
            variant="text"
            className="w-full text-black"
            startIcon={<Edit />}
          >
            Edit
          </Button>
          <Button className="w-full text-red-700" startIcon={<Delete />}>
            Delete
          </Button>
        </div>
      </div>
    </div>
  );
}
