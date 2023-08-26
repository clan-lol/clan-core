"use client";

import * as React from "react";
import Box from "@mui/material/Box";
import DeleteIcon from "@mui/icons-material/Delete";
import SpeedDial, { CloseReason, OpenReason } from "@mui/material/SpeedDial";
import SpeedDialIcon from "@mui/material/SpeedDialIcon";
import SpeedDialAction from "@mui/material/SpeedDialAction";
import EditIcon from "@mui/icons-material/ModeEdit";
import AddIcon from "@mui/icons-material/Add";
import Link from "next/link";

export function StickySpeedDial(props: { selected: string | undefined }) {
  const { selected } = props;
  const [open, setOpen] = React.useState(false);

  function handleClose(event: any, reason: CloseReason) {
    if (reason === "toggle" || reason === "escapeKeyDown") {
      setOpen(false);
    }
  }

  function handleOpen(event: any, reason: OpenReason) {
    if (reason === "toggle") {
      setOpen(true);
    }
  }

  const isSomethingSelected = selected != undefined;

  function editDial() {
    if (isSomethingSelected) {
      return (
        <Link href={`/machines/edit/${selected}`} style={{ marginTop: 7.5 }}>
          <EditIcon color="action" />
        </Link>
      );
    } else {
      return <EditIcon color="disabled" />;
    }
  }

  return (
    <Box
      sx={{
        transform: "translateZ(0px)",
        flexGrow: 1,
        position: "fixed",
        right: 20,
        top: 15,
        margin: 0,
        zIndex: 9000,
      }}
    >
      <SpeedDial
        color="secondary"
        ariaLabel="SpeedDial basic example"
        icon={<SpeedDialIcon />}
        direction="down"
        onClose={handleClose}
        onOpen={handleOpen}
        open={open}
      >
        <SpeedDialAction
          key="Add"
          icon={
            <Link href="/machines/add" style={{ marginTop: 7.5 }}>
              <AddIcon color="action" />
            </Link>
          }
          tooltipTitle="Add"
        />

        <SpeedDialAction
          key="Delete"
          icon={
            <DeleteIcon color={isSomethingSelected ? "action" : "disabled"} />
          }
          tooltipTitle="Delete"
        />
        <SpeedDialAction key="Edit" icon={editDial()} tooltipTitle="Edit" />
      </SpeedDial>
    </Box>
  );
}
