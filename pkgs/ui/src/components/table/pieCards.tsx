import { Card, CardContent, Stack, Typography } from "@mui/material";
import hexRgb from "hex-rgb";
import { useMemo } from "react";

interface PieData {
  name: string;
  value: number;
  color: string;
}

interface PieCardsProps {
  pieData: PieData[];
}

export function PieCards(props: PieCardsProps) {
  const { pieData } = props;

  const cardData = useMemo(() => {
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
      sx={{ paddingTop: 6 }}
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
