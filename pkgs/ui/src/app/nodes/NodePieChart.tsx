import React from "react";
import {
  PieChart,
  Pie,
  Sector,
  Cell,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { useTheme } from "@mui/material/styles";
import { Box, Color } from "@mui/material";

export interface PieData {
  name: string;
  value: number;
  color: string;
}

interface Props {
  data: PieData[];
  showLabels?: boolean;
}

export default function NodePieChart(props: Props) {
  const theme = useTheme();
  const { data, showLabels } = props;

  return (
    <Box height={350}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            innerRadius={85}
            outerRadius={120}
            fill={theme.palette.primary.main}
            dataKey="value"
            nameKey="name"
            label={showLabels}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Legend verticalAlign="bottom" />
        </PieChart>
      </ResponsiveContainer>
    </Box>
  );
}
