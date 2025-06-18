import cx from "classnames";
import { Component, JSX, Show, splitProps } from "solid-js";
import ArrowBottom from "@/icons/arrow-bottom.svg";
import ArrowLeft from "@/icons/arrow-left.svg";
import ArrowRight from "@/icons/arrow-right.svg";
import ArrowTop from "@/icons/arrow-top.svg";
import Attention from "@/icons/attention.svg";
import CaretDown from "@/icons/caret-down.svg";
import CaretLeft from "@/icons/caret-left.svg";
import CaretRight from "@/icons/caret-right.svg";
import CaretUp from "@/icons/caret-up.svg";
import Checkmark from "@/icons/checkmark.svg";
import ClanIcon from "@/icons/clan-icon.svg";
import Cursor from "@/icons/cursor.svg";
import Close from "@/icons/close.svg";
import Download from "@/icons/download.svg";
import Edit from "@/icons/edit.svg";
import Expand from "@/icons/expand.svg";
import EyeClose from "@/icons/eye-close.svg";
import EyeOpen from "@/icons/eye-open.svg";
import Filter from "@/icons/filter.svg";
import Flash from "@/icons/flash.svg";
import Folder from "@/icons/folder.svg";
import Grid from "@/icons/grid.svg";
import Info from "@/icons/info.svg";
import List from "@/icons/list.svg";
import Load from "@/icons/load.svg";
import More from "@/icons/more.svg";
import Paperclip from "@/icons/paperclip.svg";
import Plus from "@/icons/plus.svg";
import Reload from "@/icons/reload.svg";
import Report from "@/icons/report.svg";
import Search from "@/icons/search.svg";
import Settings from "@/icons/settings.svg";
import Trash from "@/icons/trash.svg";
import Update from "@/icons/update.svg";
import WarningFilled from "@/icons/warning-filled.svg";
import Modules from "@/icons/modules.svg";
import NewMachine from "@/icons/new-machine.svg";
import AI from "@/icons/ai.svg";
import User from "@/icons/user.svg";
import Heart from "@/icons/heart.svg";
import SearchFilled from "@/icons/search-filled.svg";
import Offline from "@/icons/offline.svg";
import Switch from "@/icons/switch.svg";
import Tag from "@/icons/tag.svg";
import Machine from "@/icons/machine.svg";
import Loader from "@/icons/loader.svg";
import { Dynamic } from "solid-js/web";

const icons = {
  AI,
  ArrowBottom,
  ArrowLeft,
  ArrowRight,
  ArrowTop,
  Attention,
  CaretDown,
  CaretLeft,
  CaretRight,
  CaretUp,
  Checkmark,
  ClanIcon,
  Close,
  Cursor,
  Download,
  Edit,
  Expand,
  EyeClose,
  EyeOpen,
  Filter,
  Flash,
  Folder,
  Grid,
  Heart,
  Info,
  List,
  Load,
  Machine,
  Modules,
  More,
  NewMachine,
  Offline,
  Paperclip,
  Plus,
  Reload,
  Report,
  Search,
  SearchFilled,
  Settings,
  Switch,
  Tag,
  Trash,
  Update,
  User,
  WarningFilled,
};

export type IconVariant = keyof typeof icons;

export interface IconProps extends JSX.SvgSVGAttributes<SVGElement> {
  icon: IconVariant;
  class?: string;
  size?: number | string;
}

const Icon: Component<IconProps> = (props) => {
  const [local, iconProps] = splitProps(props, ["icon", "class"]);

  const IconComponent = () => icons[local.icon];

  return IconComponent() ? (
    <Dynamic
      component={IconComponent()}
      class={cx("icon", local.class)}
      width={iconProps.size || "1em"}
      height={iconProps.size || "1em"}
      viewBox="0 0 48 48"
      // @ts-expect-error: dont know, fix this type nit later
      ref={iconProps.ref}
      {...iconProps}
    />
  ) : undefined;
};

export default Icon;
