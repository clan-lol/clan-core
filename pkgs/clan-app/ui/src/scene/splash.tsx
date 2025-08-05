import Logo from "@/logos/darknet-builder-logo.svg";
import styles from "./splash.module.css";
import { Typography } from "../components/Typography/Typography";
import { LoadingBar } from "../components/LoadingBar/LoadingBar";

export const Splash = () => (
  <div class={styles.splash}>
    <div class={styles.splash_content}>
      <span class={styles.splash_title}>
        <Logo />
      </span>
      <LoadingBar />

      <Typography hierarchy="label" size="xs" weight="medium">
        Loading new Clan
      </Typography>
    </div>
  </div>
);
