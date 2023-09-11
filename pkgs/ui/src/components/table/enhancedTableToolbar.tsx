"use client";

import React, { useMemo } from "react";
import Box from "@mui/material/Box";
import Grid2 from "@mui/material/Unstable_Grid2";
import useMediaQuery from "@mui/material/useMediaQuery";
import { useTheme } from "@mui/material";

import { PieCards } from "./pieCards";
import { PieData, NodePieChart } from "./nodePieChart";
import { Machine } from "@/api/model/machine";
import { Status } from "@/api/model";

interface EnhancedTableToolbarProps {
  tableData: readonly Machine[];
}

export function EnhancedTableToolbar(
  props: React.PropsWithChildren<EnhancedTableToolbarProps>,
) {
  const { tableData } = props;
  const theme = useTheme();
  const is_lg = useMediaQuery(theme.breakpoints.down("lg"));

  const pieData: PieData[] = useMemo(() => {
    const online = tableData.filter(
      (row) => row.status === Status.online,
    ).length;
    const offline = tableData.filter(
      (row) => row.status === Status.offline,
    ).length;
    const pending = tableData.filter(
      (row) => row.status === Status.unknown,
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
