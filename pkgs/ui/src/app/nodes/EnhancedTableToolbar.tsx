"use client";

import * as React from "react";
import Box from "@mui/material/Box";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import FormControlLabel from "@mui/material/FormControlLabel";
import Switch from "@mui/material/Switch";
import Stack from "@mui/material/Stack/Stack";
import NodePieChart from "./NodePieChart";

import Grid2 from "@mui/material/Unstable_Grid2"; // Grid version 2
import { Card, CardContent, FormGroup, useTheme } from "@mui/material";
import hexRgb from "hex-rgb";
import useMediaQuery from "@mui/material/useMediaQuery";
import { NodeStatus, TableData } from "@/data/nodeData";

interface EnhancedTableToolbarProps {
  tableData: TableData[];
}

function PieCardData(props: { pieData: PieData[]; debugSx: any }) {
  const { pieData, debugSx } = props;

  const cardData = React.useMemo(() => {
    return pieData
      .filter((pieItem) => pieItem.value > 0)
      .concat({
        name: "Total",
        value: pieData.reduce((a, b) => a + b.value, 0),
        color: "#000000",
      });
  }, [pieData]);

  return (
    <Stack
      sx={{ ...debugSx, paddingTop: 6 }}
      height={350}
      id="cardBox"
      display="flex"
      flexDirection="column"
      justifyContent="flex-start"
      flexWrap="wrap"
    >
      {cardData.map((pieItem) => (
        <Card
          key={pieItem.name}
          sx={{
            marginBottom: 2,
            marginRight: 2,
            width: 110,
            height: 110,
            backgroundColor: hexRgb(pieItem.color, {
              format: "css",
              alpha: 0.25,
            }),
          }}
        >
          <CardContent>
            <Typography
              variant="h4"
              component="div"
              gutterBottom={true}
              textAlign="center"
            >
              {pieItem.value}
            </Typography>
            <Typography
              sx={{ mb: 1.5 }}
              color="text.secondary"
              textAlign="center"
            >
              {pieItem.name}
            </Typography>
          </CardContent>
        </Card>
      ))}
    </Stack>
  );
}

interface PieData {
  name: string;
  value: number;
  color: string;
}

export default function EnhancedTableToolbar(
  props: React.PropsWithChildren<EnhancedTableToolbarProps>,
) {
  const { tableData } = props;
  const theme = useTheme();
  const is_lg = useMediaQuery(theme.breakpoints.down("lg"));
  const [debug, setDebug] = React.useState<boolean>(false);

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

  const pieData: PieData[] = React.useMemo(() => {
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
    <Grid2 container spacing={1} sx={debugSx}>
      <Grid2 key="Header" xs={6}>
        <Typography
          sx={{ marginLeft: 3, marginTop: 1 }}
          variant="h6"
          id="tableTitle"
          component="div"
        >
          NODES
        </Typography>
      </Grid2>
      {/* Debug Controls */}
      <Grid2 key="Debug-Controls" xs={6} justifyContent="left" display="flex">
        <FormGroup>
          <FormControlLabel
            control={
              <Switch
                onChange={() => {
                  setDebug(!debug);
                }}
                checked={debug}
              />
            }
            label="Debug"
          />
        </FormGroup>
      </Grid2>

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
        <PieCardData pieData={pieData} debugSx={debugSx} />
      </Grid2>

      {/*Toolbar Grid */}
      <Grid2 key="Toolbar" xs={12}>
        <Toolbar
          sx={{
            pl: { sm: 2 },
            pr: { xs: 1, sm: 1 },
          }}
        >
          {props.children}
        </Toolbar>
      </Grid2>
    </Grid2>
  );
}
