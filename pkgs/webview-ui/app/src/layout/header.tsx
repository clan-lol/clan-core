import { JSX } from "solid-js";
import { Typography } from "../components/Typography";
import { BackButton } from "../components/BackButton";

interface HeaderProps {
  title: string;
  toolbar?: JSX.Element;
  showBack?: boolean;
}
export const Header = (props: HeaderProps) => {
  return (
    <div class="sticky top-0 z-20 flex items-center border-b bg-white/80 px-6 py-4 backdrop-blur-md border-def-3">
      <div class="flex-none">
        {props.showBack && <BackButton />}
        <span class=" lg:hidden" data-tip="Menu">
          <label class=" " for="toplevel-drawer">
            <span class="material-icons">menu</span>
          </label>
        </span>
      </div>
      <div class="flex-1">
        <Typography hierarchy="title" size="m" weight="medium" class="">
          {props.title}
        </Typography>
      </div>
      <div class="flex items-center justify-center gap-3">{props.toolbar}</div>
    </div>
  );
};
