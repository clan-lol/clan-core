import { DashboardCard } from "../../components/card";
import { Grid } from "@mui/material";
import { Button } from "@mui/material";

export default function Dashboard() {
  return (
    <Grid container>
      <Grid item xs={12}>
        <DashboardCard />
        <Button variant="contained" color="primary">
          Click me!
        </Button>
        Hallo Mike !
      </Grid>
      <Grid item xs={6}>
        <DashboardCard />
        Server Stats
      </Grid>
      <Grid item xs={6}>
        Network Stats
        <DashboardCard />
      </Grid>
    </Grid>
  );
}
