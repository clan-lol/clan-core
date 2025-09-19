import cx from "classnames";
import { Component, JSX, mergeProps, splitProps } from "solid-js";

import Address from "@/icons/address.svg";
import AI from "@/icons/ai.svg";
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
import CheckSolid from "@/icons/check-solid.svg";
import ClanIcon from "@/icons/clan-icon.svg";
import Close from "@/icons/close.svg";
import CloseCircle from "@/icons/close-circle.svg";
import Code from "@/icons/code.svg";
import Cursor from "@/icons/cursor.svg";
import Download from "@/icons/download.svg";
import Edit from "@/icons/edit.svg";
import Expand from "@/icons/expand.svg";
import EyeClose from "@/icons/eye-close.svg";
import EyeOpen from "@/icons/eye-open.svg";
import Filter from "@/icons/filter.svg";
import Flash from "@/icons/flash.svg";
import Folder from "@/icons/folder.svg";
import General from "@/icons/general.svg";
import Grid from "@/icons/grid.svg";
import Heart from "@/icons/heart.svg";
import Info from "@/icons/info.svg";
import List from "@/icons/list.svg";
import Load from "@/icons/load.svg";
import Machine from "@/icons/machine.svg";
import Minimize from "@/icons/minimize.svg";
import Modules from "@/icons/modules.svg";
import More from "@/icons/more.svg";
import NewMachine from "@/icons/new-machine.svg";
import Offline from "@/icons/offline.svg";
import Paperclip from "@/icons/paperclip.svg";
import Plus from "@/icons/plus.svg";
import Reload from "@/icons/reload.svg";
import Report from "@/icons/report.svg";
import Search from "@/icons/search.svg";
import SearchFilled from "@/icons/search-filled.svg";
import Services from "@/icons/services.svg";
import Settings from "@/icons/settings.svg";
import Switch from "@/icons/switch.svg";
import Tag from "@/icons/tag.svg";
import Trash from "@/icons/trash.svg";
import Update from "@/icons/update.svg";
import User from "@/icons/user.svg";
import WarningFilled from "@/icons/warning-filled.svg";

import { Dynamic } from "solid-js/web";
import styles from "./Icon.module.css";
import { Color } from "../colors";
import colorsStyles from "../colors.module.css";
import { getInClasses } from "@/src/util";

const icons = {
  Address,
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
  CheckSolid,
  ClanIcon,
  Close,
  CloseCircle,
  Code,
  Cursor,
  Download,
  Edit,
  Expand,
  EyeClose,
  EyeOpen,
  Filter,
  Flash,
  Folder,
  General,
  Grid,
  Heart,
  Info,
  List,
  Load,
  Machine,
  Minimize,
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
  Services,
  Settings,
  Switch,
  Tag,
  Trash,
  Update,
  User,
  WarningFilled,
};

export type IconVariant = keyof typeof icons;

const viewBoxes: Partial<Record<IconVariant, string>> = {
  ClanIcon: "0 0 72 89",
};

type In =
  | "Button"
  | "Button-primary"
  | "Button-secondary"
  | "Button-s"
  | "Button-xs"
  | "MachineTags"
  | "MachineTags-s"
  | "ConfigureRole"
  // TODO: better name
  | "WorkflowPanelTitle"
  | "SidebarBody-AccordionTrigger";
export interface IconProps extends JSX.SvgSVGAttributes<SVGElement> {
  icon: IconVariant;
  size?: number | string;
  color?: Color;
  inverted?: boolean;
  in?: In | In[];
}

const Icon: Component<IconProps> = (props) => {
  const [local, iconProps] = splitProps(
    mergeProps({ color: "primary", size: "1em" } as const, props),
    ["icon", "color", "size", "inverted", "in"],
  );
  const component = () => icons[local.icon];
  // we need to adjust the view box for certain icons
  const viewBox = () => viewBoxes[local.icon] || "0 0 48 48";
  return (
    <Dynamic
      component={component()}
      class={cx(
        styles.icon,
        getInClasses(styles, local.in),
        colorsStyles[local.color],
        {
          [colorsStyles.inverted]: local.inverted,
        },
      )}
      data-icon-name={local.icon}
      width={local.size}
      height={local.size}
      viewBox={viewBox()}
      ref={iconProps.ref}
      {...iconProps}
    />
  );
};

export default Icon;
