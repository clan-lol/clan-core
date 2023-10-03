import { Hct } from "@material/material-color-utilities";

export type BaseColors = {
    neutral: BaseColor;
    red: BaseColor;
    green: BaseColor;
    yellow: BaseColor;
    purple: BaseColor;
    blue: BaseColor;
};

export type BaseColor = {
    keyColor: HexString;
    tones: number[];
    follows?: string;
};

export type ColorSet = { [key: string]: ColorDesignToken };

/** The resolved alias tokens
 *
 * @example
 * {
 *  primary: "blue"
 * ...
 * }
 *
 */
export type AliasMap<T extends string> = {
    [alias in T]: keyof BaseColors;
};

/** The resolved alias tokens
 *
 * @example
 * {
 *  primary0: "blue40"
 *  primary10: "blue40"
 * ...
 *  primary100: "blue100"
 * }
 *
 * Unfortunately My Typescript skills lack the ability to express this type any narrower :/
 */
export type AliasTokenMap = {
    [alias: string]: { value: string };
};

export type TonalPaletteConfig = {
    tones: number[];
};

export type HexString = string;

export type TonalPaletteItem = {
    /**
     * @example
     * 20
     */
    shade: number;
    /**
     * @example
     * "blue20"
     */
    name: string;
    /**
     * @example
     * "blue"
     */
    baseName: string;
    value: Hct;
};
export type TonalPalette = TonalPaletteItem[];

export type ColorDesignToken = {
    type: "color";
    value: HexString;
    meta: {
        color: TonalPaletteItem;
        date: Date;
    };
};

export type RefTokenSystem = {
    ref: {
        palette: ColorSet;
        common: ColorSet;
        alias: AliasTokenMap;
    };
};
