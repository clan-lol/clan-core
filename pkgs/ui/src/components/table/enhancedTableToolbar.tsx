"use client";

import React, { useMemo } from "react";
import Box from "@mui/material/Box";
import Toolbar from "@mui/material/Toolbar";
import Grid2 from "@mui/material/Unstable_Grid2";
import useMediaQuery from "@mui/material/useMediaQuery";
import { useTheme } from "@mui/material";

import { NodeStatus, TableData } from "@/data/nodeData";
import { PieCards } from "./pieCards";
import { PieData, NodePieChart } from "./nodePieChart";

interface EnhancedTableToolbarProps {
  tableData: TableData[];
}

export function EnhancedTableToolbar(
  props: React.PropsWithChildren<EnhancedTableToolbarProps>,
) {
  const { tableData } = props;
  const theme = useTheme();
  const is_lg = useMediaQuery(theme.breakpoints.down("lg"));

  const pieData: PieData[] = useMemo(() => {
    const online = tableData.filter(
      (row) => row.status === NodeStatus.Online,
    ).length;
    const offline = tableData.filter(
      (row) => row.status === NodeStatus.Offline,
    ).length;
    const pending = tableData.filter(
      (row) => row.status === NodeStatus.Pending,
    ).length;

    return [
      { name: "Online", value: online, color: theme.palette.success.main },
      { name: "Offline", value: offline, color: theme.palette.error.main },
      { name: "Pending", value: pending, color: theme.palette.warning.main },
    ];
  }, [tableData, theme]);

  return (
    <Grid2 container spacing={1}>
      {/* Pie Chart Grid */}
      <Grid2
        key="PieChart"
        md={6}
        xs={12}
        display="flex"
        justifyContent="center"
        alignItems="center"
      >
        <Box height={350} width={400}>
          <NodePieChart data={pieData} showLabels={is_lg} />
        </Box>
      </Grid2>

      {/* Card Stack Grid */}
      <Grid2
        key="CardStack"
        lg={6}
        display="flex"
        sx={{ display: { lg: "flex", xs: "none", md: "flex" } }}
      >
        <PieCards pieData={pieData} />
      </Grid2>

      {/*Toolbar Grid */}
      <Grid2
        key="Toolbar"
        xs={12}
        container
        justifyContent="center"
        alignItems="center"
        sx={{ pl: { sm: 2 }, pr: { xs: 1, sm: 1 }, pt: { xs: 1, sm: 3 } }}
      >
        {props.children}
      </Grid2>
    </Grid2>
  );
}
