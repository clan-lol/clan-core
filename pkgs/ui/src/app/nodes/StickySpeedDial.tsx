"use client";

import * as React from "react";
import { alpha } from "@mui/material/styles";
import Box from "@mui/material/Box";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TablePagination from "@mui/material/TablePagination";
import TableRow from "@mui/material/TableRow";
import TableSortLabel from "@mui/material/TableSortLabel";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import Paper from "@mui/material/Paper";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";
import FormControlLabel from "@mui/material/FormControlLabel";
import Switch from "@mui/material/Switch";
import DeleteIcon from "@mui/icons-material/Delete";
import FilterListIcon from "@mui/icons-material/FilterList";
import SpeedDial, { CloseReason, OpenReason } from "@mui/material/SpeedDial";
import SpeedDialIcon from "@mui/material/SpeedDialIcon";
import SpeedDialAction from "@mui/material/SpeedDialAction";
import { visuallyHidden } from "@mui/utils";
import CircleIcon from "@mui/icons-material/Circle";
import Stack from "@mui/material/Stack/Stack";
import EditIcon from "@mui/icons-material/ModeEdit";
import SearchIcon from "@mui/icons-material/Search";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import NodePieChart, { PieData } from "./NodePieChart";
import Fab from "@mui/material/Fab";
import AddIcon from "@mui/icons-material/Add";
import Link from "next/link";

import Grid2 from "@mui/material/Unstable_Grid2"; // Grid version 2
import {
  Card,
  CardContent,
  Collapse,
  Container,
  FormGroup,
  useTheme,
} from "@mui/material";
import hexRgb from "hex-rgb";
import useMediaQuery from "@mui/material/useMediaQuery";
import { NodeStatus, NodeStatusKeys, TableData } from "@/data/nodeData";
import { jsx } from "@emotion/react";

export default function StickySpeedDial(props: {
  selected: string | undefined;
}) {
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
        <Link href="/nodes/edit" style={{ marginTop: 7.5 }}>
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
            <Link href="/nodes/add" style={{ marginTop: 7.5 }}>
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
