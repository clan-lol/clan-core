import { Tooltip } from "@/src/components/Tooltip/Tooltip";
import { Typography } from "@/src/components/Typography/Typography";

import "./Creating.css";

export const Creating = () => (
  <div class="creating">
    <Tooltip open={true} placement="top" trigger={<div />}>
      <Typography hierarchy="body" size="xs" weight="medium" inverted={true}>
        Your Clan is being created
      </Typography>
    </Tooltip>

    <div class="scene">
      <div class="frame">
        <div id="cube-1" class="cube state-1">
          <div class="cube-face front"></div>
          <div class="cube-face left"></div>
          <div class="cube-face right"></div>
          <div class="cube-face top"></div>
          <div class="cube-face bottom"></div>
          <div class="cube-face back"></div>
        </div>

        <div id="cube-2" class="cube state-2">
          <div class="cube-face front"></div>
          <div class="cube-face left"></div>
          <div class="cube-face right"></div>
          <div class="cube-face top"></div>
          <div class="cube-face bottom"></div>
          <div class="cube-face back"></div>
        </div>

        <div id="cube-3" class="cube state-3">
          <div class="cube-face front"></div>
          <div class="cube-face left"></div>
          <div class="cube-face right"></div>
          <div class="cube-face top"></div>
          <div class="cube-face bottom"></div>
          <div class="cube-face back"></div>
        </div>

        <div id="cube-4" class="cube state-4">
          <div class="cube-face front"></div>
          <div class="cube-face left"></div>
          <div class="cube-face right"></div>
          <div class="cube-face top"></div>
          <div class="cube-face bottom"></div>
          <div class="cube-face back"></div>
        </div>

        <div id="cube-1-1" class="cube state-1-1">
          <div class="cube-face front"></div>
          <div class="cube-face left"></div>
          <div class="cube-face right"></div>
          <div class="cube-face top"></div>
          <div class="cube-face bottom"></div>
          <div class="cube-face back"></div>
        </div>

        <div id="cube-2-2" class="cube state-2-2">
          <div class="cube-face front"></div>
          <div class="cube-face left"></div>
          <div class="cube-face right"></div>
          <div class="cube-face top"></div>
          <div class="cube-face bottom"></div>
          <div class="cube-face back"></div>
        </div>

        <div id="cube-3-3" class="cube state-3-3">
          <div class="cube-face front"></div>
          <div class="cube-face left"></div>
          <div class="cube-face right"></div>
          <div class="cube-face top"></div>
          <div class="cube-face bottom"></div>
          <div class="cube-face back"></div>
        </div>

        <div id="cube-4-4" class="cube state-4-4">
          <div class="cube-face front"></div>
          <div class="cube-face left"></div>
          <div class="cube-face right"></div>
          <div class="cube-face top"></div>
          <div class="cube-face bottom"></div>
          <div class="cube-face back"></div>
        </div>
      </div>
    </div>
  </div>
);
