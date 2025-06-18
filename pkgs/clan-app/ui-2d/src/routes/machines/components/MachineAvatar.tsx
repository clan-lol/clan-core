import { RndThumbnail } from "@/src/components/noiseThumbnail";
import cx from "classnames";
interface AvatarProps {
  name?: string;
  class?: string;
}
export const MachineAvatar = (props: AvatarProps) => {
  return (
    <figure>
      <div class="">
        <div
          class={cx(
            "rounded-lg border p-2 bg-def-1 border-def-3 h-fit",
            props.class,
          )}
        >
          <RndThumbnail name={props.name || ""} height={120} width={220} />
        </div>
      </div>
    </figure>
  );
};
