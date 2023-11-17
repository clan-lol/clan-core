"use client";

import { CircularProgress, Grid } from "@mui/material";
import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";
import TablePagination from "@mui/material/TablePagination";
import { ChangeEvent, useState } from "react";

import { useMachines } from "../hooks/useMachines";
import { NodeTableContainer } from "./nodeTableContainer";
import { SearchBar } from "./searchBar";

export function NodeTable() {
  const { isLoading, data: machines, rawData, setFilters } = useMachines();

  const [selected, setSelected] = useState<string | undefined>(undefined);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  if (isLoading) {
    return (
      <Grid
        container
        sx={{
          h: "100vh",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <CircularProgress size={80} color="secondary" />
      </Grid>
    );
  }

  return (
    <Box sx={{ width: "100%" }}>
      <Paper sx={{ width: "100%", mb: 2, p: { xs: 0, lg: 2 } }} elevation={0}>
        <SearchBar
          allData={rawData?.data.machines || []}
          setQuery={setFilters}
        />
        <NodeTableContainer
          tableData={machines}
          page={page}
          rowsPerPage={rowsPerPage}
          dense={false}
          selected={selected}
          setSelected={setSelected}
        />

        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={machines.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>
    </Box>
  );
}
