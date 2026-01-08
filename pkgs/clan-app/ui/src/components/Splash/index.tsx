import styles from "./Splash.module.css";
import { Typography } from "../Typography/Typography";
import { LoadingBar } from "../LoadingBar/LoadingBar";

export default function Splash() {
  return (
    <div class={styles.splash}>
      <div class={styles.splash_content}>
        <Typography hierarchy="label" size="s" weight="medium">
          Loading Clan
        </Typography>
        <LoadingBar />
      </div>
    </div>
  );
}
