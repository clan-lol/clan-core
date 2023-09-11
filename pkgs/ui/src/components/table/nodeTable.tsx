"use client";

import { useState, ChangeEvent, useMemo } from "react";
import Box from "@mui/material/Box";
import TablePagination from "@mui/material/TablePagination";
import Paper from "@mui/material/Paper";
import { CircularProgress, Grid, useTheme } from "@mui/material";
import useMediaQuery from "@mui/material/useMediaQuery";

import { EnhancedTableToolbar } from "./enhancedTableToolbar";
import { StickySpeedDial } from "./stickySpeedDial";
import { NodeTableContainer } from "./nodeTableContainer";
import { SearchBar } from "./searchBar";
import Grid2 from "@mui/material/Unstable_Grid2/Grid2";
import { useMachines } from "../hooks/useMachines";
import { Machine } from "@/api/model/machine";

export function NodeTable() {
  const machines = useMachines();

  const theme = useTheme();
  const is_xs = useMediaQuery(theme.breakpoints.only("xs"));

  const [selected, setSelected] = useState<string | undefined>(undefined);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [filteredList, setFilteredList] = useState<readonly Machine[]>([]);

  const tableData = useMemo(() => {
    const tableData = machines.data.map((machine) => {
      return { name: machine.name, status: machine.status };
    });
    setFilteredList(tableData);
    return tableData;
  }, [machines.data]);

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  if (machines.isLoading) {
    return (
      <Grid
        container
        style={{ height: "100vh" }} // make the container fill the screen height
        alignItems="center" // center the items vertically
        justifyContent="center" // center the items horizontally
      >
        <CircularProgress size={80} color="secondary" />
      </Grid>
    );
  } else {
    return (
      <Box sx={{ width: "100%" }}>
        <Paper sx={{ width: "100%", mb: 2 }}>
          <StickySpeedDial selected={selected} />
          <EnhancedTableToolbar tableData={tableData}>
            <Grid2 xs={12}>
              <SearchBar
                tableData={tableData}
                setFilteredList={setFilteredList}
              />
            </Grid2>
          </EnhancedTableToolbar>

          <NodeTableContainer
            tableData={filteredList}
            page={page}
            rowsPerPage={rowsPerPage}
            dense={false}
            selected={selected}
            setSelected={setSelected}
          />

          {/* TODO: This creates the error Warning: Prop `id` did not match. Server: ":RspmmcqH1:" Client: ":R3j6qpj9H1:" */}
          <TablePagination
            rowsPerPageOptions={[5, 10, 25]}
            labelRowsPerPage={is_xs ? "Rows" : "Rows per page:"}
            component="div"
            count={filteredList.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </Paper>
      </Box>
    );
  }
}
