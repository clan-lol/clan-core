import styles from "./CubeConstruction.module.css";
import cx from "classnames";

export const CubeConstruction = () => (
  <div class={styles.cubeConstruction}>
    <div class={styles.scene}>
      <div class={cx(styles.cube, styles.cube1Front)}>
        <div class={cx(styles.face, styles.front)}></div>
        <div class={cx(styles.face, styles.left)}></div>
        <div class={cx(styles.face, styles.right)}></div>
        <div class={cx(styles.face, styles.top)}></div>
        <div class={cx(styles.face, styles.bottom)}></div>
        <div class={cx(styles.face, styles.back)}></div>
      </div>
      <div class={cx(styles.cube, styles.cube1Rear)}>
        <div class={cx(styles.face, styles.front)}></div>
        <div class={cx(styles.face, styles.left)}></div>
        <div class={cx(styles.face, styles.right)}></div>
        <div class={cx(styles.face, styles.top)}></div>
        <div class={cx(styles.face, styles.bottom)}></div>
        <div class={cx(styles.face, styles.back)}></div>
      </div>

      <div class={cx(styles.cube, styles.cube2Front)}>
        <div class={cx(styles.face, styles.front)}></div>
        <div class={cx(styles.face, styles.left)}></div>
        <div class={cx(styles.face, styles.right)}></div>
        <div class={cx(styles.face, styles.top)}></div>
        <div class={cx(styles.face, styles.bottom)}></div>
        <div class={cx(styles.face, styles.back)}></div>
      </div>

      <div class={cx(styles.cube, styles.cube2Rear)}>
        <div class={cx(styles.face, styles.front)}></div>
        <div class={cx(styles.face, styles.left)}></div>
        <div class={cx(styles.face, styles.right)}></div>
        <div class={cx(styles.face, styles.top)}></div>
        <div class={cx(styles.face, styles.bottom)}></div>
        <div class={cx(styles.face, styles.back)}></div>
      </div>

      <div class={cx(styles.cube, styles.cube3Front)}>
        <div class={cx(styles.face, styles.front)}></div>
        <div class={cx(styles.face, styles.left)}></div>
        <div class={cx(styles.face, styles.right)}></div>
        <div class={cx(styles.face, styles.top)}></div>
        <div class={cx(styles.face, styles.bottom)}></div>
        <div class={cx(styles.face, styles.back)}></div>
      </div>

      <div class={cx(styles.cube, styles.cube3Rear)}>
        <div class={cx(styles.face, styles.front)}></div>
        <div class={cx(styles.face, styles.left)}></div>
        <div class={cx(styles.face, styles.right)}></div>
        <div class={cx(styles.face, styles.top)}></div>
        <div class={cx(styles.face, styles.bottom)}></div>
        <div class={cx(styles.face, styles.back)}></div>
      </div>

      <div class={cx(styles.cube, styles.cube4Front)}>
        <div class={cx(styles.face, styles.front)}></div>
        <div class={cx(styles.face, styles.left)}></div>
        <div class={cx(styles.face, styles.right)}></div>
        <div class={cx(styles.face, styles.top)}></div>
        <div class={cx(styles.face, styles.bottom)}></div>
        <div class={cx(styles.face, styles.back)}></div>
      </div>

      <div class={cx(styles.cube, styles.cube4Rear)}>
        <div class={cx(styles.face, styles.front)}></div>
        <div class={cx(styles.face, styles.left)}></div>
        <div class={cx(styles.face, styles.right)}></div>
        <div class={cx(styles.face, styles.top)}></div>
        <div class={cx(styles.face, styles.bottom)}></div>
        <div class={cx(styles.face, styles.back)}></div>
      </div>
    </div>
  </div>
);
