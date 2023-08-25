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
import StickySpeedDial from "./StickySpeedDial";
import { jsx } from "@emotion/react";

export default function Row(props: {
  row: TableData;
  selected: string | undefined;
  setSelected: (a: string | undefined) => void;
}) {
  function renderStatus(status: NodeStatusKeys) {
    switch (status) {
      case NodeStatus.Online:
        return (
          <Stack direction="row" alignItems="center" gap={1}>
            <CircleIcon color="success" style={{ fontSize: 15 }} />
            <Typography component="div" align="left" variant="body1">
              Online
            </Typography>
          </Stack>
        );

      case NodeStatus.Offline:
        return (
          <Stack direction="row" alignItems="center" gap={1}>
            <CircleIcon color="error" style={{ fontSize: 15 }} />
            <Typography component="div" align="left" variant="body1">
              Offline
            </Typography>
          </Stack>
        );
      case NodeStatus.Pending:
        return (
          <Stack direction="row" alignItems="center" gap={1}>
            <CircleIcon color="warning" style={{ fontSize: 15 }} />
            <Typography component="div" align="left" variant="body1">
              Pending
            </Typography>
          </Stack>
        );
    }
  }

  const { row, selected, setSelected } = props;
  const [open, setOpen] = React.useState(false);
  //const labelId = `enhanced-table-checkbox-${index}`;

  // Speed optimization. We compare string pointers here instead of the string content.
  const isSelected = selected == row.name;

  const handleClick = (event: React.MouseEvent<unknown>, name: string) => {
    if (isSelected) {
      setSelected(undefined);
    } else {
      setSelected(name);
    }
  };

  const debug = true;
  const debugSx = debug
    ? {
        "--Grid-borderWidth": "1px",
        borderTop: "var(--Grid-borderWidth) solid",
        borderLeft: "var(--Grid-borderWidth) solid",
        borderColor: "divider",
        "& > div": {
          borderRight: "var(--Grid-borderWidth) solid",
          borderBottom: "var(--Grid-borderWidth) solid",
          borderColor: "divider",
        },
      }
    : {};

  return (
    <React.Fragment>
      {/* Rendered Row */}
      <TableRow
        hover
        role="checkbox"
        aria-checked={isSelected}
        tabIndex={-1}
        key={row.name}
        selected={isSelected}
        sx={{ cursor: "pointer" }}
      >
        <TableCell padding="none">
          <IconButton
            aria-label="expand row"
            size="small"
            onClick={() => setOpen(!open)}
          >
            {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
          </IconButton>
        </TableCell>
        <TableCell
          component="th"
          scope="row"
          onClick={(event) => handleClick(event, row.name)}
        >
          <Stack>
            <Typography component="div" align="left" variant="body1">
              {row.name}
            </Typography>
            <Typography
              color="grey"
              component="div"
              align="left"
              variant="body2"
            >
              {row.id}
            </Typography>
          </Stack>
        </TableCell>
        <TableCell
          align="right"
          onClick={(event) => handleClick(event, row.name)}
        >
          {renderStatus(row.status)}
        </TableCell>
        <TableCell
          align="right"
          onClick={(event) => handleClick(event, row.name)}
        >
          <Typography component="div" align="left" variant="body1">
            {row.last_seen} days ago
          </Typography>
        </TableCell>
      </TableRow>

      {/* Row Expansion */}
      <TableRow>
        <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={6}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box sx={{ margin: 1 }}>
              <Typography variant="h6" gutterBottom component="div">
                Metadata
              </Typography>
              <Grid2 container spacing={2} paddingLeft={0}>
                <Grid2
                  xs={6}
                  style={{ ...debugSx }}
                  justifyContent="left"
                  display="flex"
                  paddingRight={3}
                >
                  <Box>Hello1</Box>
                </Grid2>
                <Grid2 xs={6} style={{ ...debugSx }} paddingLeft={6}>
                  <Box>Hello2</Box>
                </Grid2>
              </Grid2>
            </Box>
          </Collapse>
        </TableCell>
      </TableRow>
    </React.Fragment>
  );
}
