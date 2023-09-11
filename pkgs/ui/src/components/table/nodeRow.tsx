"use client";

import * as React from "react";
import Box from "@mui/material/Box";
import TableCell from "@mui/material/TableCell";
import TableRow from "@mui/material/TableRow";
import Typography from "@mui/material/Typography";
import IconButton from "@mui/material/IconButton";
import CircleIcon from "@mui/icons-material/Circle";
import Stack from "@mui/material/Stack/Stack";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import Grid2 from "@mui/material/Unstable_Grid2"; // Grid version 2
import { Collapse } from "@mui/material";
import { Machine, Status } from "@/api/model";

function renderStatus(status: Status) {
  switch (status) {
    case Status.online:
      return (
        <Stack direction="row" alignItems="center" gap={1}>
          <CircleIcon color="success" style={{ fontSize: 15 }} />
          <Typography component="div" align="left" variant="body1">
            Online
          </Typography>
        </Stack>
      );

    case Status.offline:
      return (
        <Stack direction="row" alignItems="center" gap={1}>
          <CircleIcon color="error" style={{ fontSize: 15 }} />
          <Typography component="div" align="left" variant="body1">
            Offline
          </Typography>
        </Stack>
      );
    case Status.unknown:
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
export function NodeRow(props: {
  row: Machine;
  selected: string | undefined;
  setSelected: (a: string | undefined) => void;
}) {
  const { row, selected, setSelected } = props;
  const [open, setOpen] = React.useState(false);

  // Speed optimization. We compare string pointers here instead of the string content.
  const isSelected = selected == row.name;

  const handleClick = (event: React.MouseEvent<unknown>, name: string) => {
    if (isSelected) {
      setSelected(undefined);
    } else {
      setSelected(name);
    }
  };

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
          </Stack>
        </TableCell>
        <TableCell
          align="right"
          onClick={(event) => handleClick(event, row.name)}
        >
          {renderStatus(row.status)}
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
                  justifyContent="left"
                  display="flex"
                  paddingRight={3}
                >
                  <Box>Hello1</Box>
                </Grid2>
                <Grid2 xs={6} paddingLeft={6}>
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
