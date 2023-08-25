"use client";

import * as React from "react";
import Box from "@mui/material/Box";
import TablePagination from "@mui/material/TablePagination";
import Paper from "@mui/material/Paper";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";
import SearchIcon from "@mui/icons-material/Search";
import NodeTableContainer from "./NodeTableContainer";

import { useTheme } from "@mui/material";
import useMediaQuery from "@mui/material/useMediaQuery";
import { TableData } from "@/data/nodeData";
import EnhancedTableToolbar from "./EnhancedTableToolbar";
import { table } from "console";

function SearchBar() {
  const [search, setSearch] = React.useState<string | undefined>(undefined);

  const handleSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(event.target.value);
  };

  return (
    <label htmlFor="search">
      <Tooltip title="Filter list">
        <IconButton>
          <SearchIcon />
        </IconButton>
      </Tooltip>
      <input id="search" type="text" value={search} onChange={handleSearch} />
    </label>
  );
}

export interface NodeTableProps {
  tableData: TableData[];
}

export default function NodeTable(props: NodeTableProps) {
  let { tableData } = props;

  const theme = useTheme();
  const is_xs = useMediaQuery(theme.breakpoints.only("xs"));

  const [selected, setSelected] = React.useState<string | undefined>(undefined);
  const [page, setPage] = React.useState(0);
  const [rowsPerPage, setRowsPerPage] = React.useState(5);

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  return (
    <Box sx={{ width: "100%" }}>
      <Paper sx={{ width: "100%", mb: 2 }}>
        <EnhancedTableToolbar tableData={tableData} selected={selected} />
        <NodeTableContainer
          tableData={tableData}
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
          count={tableData.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>
    </Box>
  );
}
