import Logo from "@/logos/darknet-builder-logo.svg";
import "./splash.css";
import { Typography } from "../components/Typography/Typography";

export const Splash = () => (
  <div id="splash">
    <div class="content">
      <span class="title">
        <Logo />
      </span>
      <div class="loader"></div>

      <Typography hierarchy="label" size="xs" weight="medium">
        Loading new Clan
      </Typography>
    </div>
  </div>
);
