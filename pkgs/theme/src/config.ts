import { AliasMap, BaseColors, HexString } from "./types.js";

export type PaletteConfig = {
    baseColors: BaseColors;
    tones: number[];
    aliases: AliasMap<"primary" | "secondary" | "error">;
    common: {
        // Black and white is always constant
        // We declare this on the type level
        white: "#ffffff";
        black: "#000000";
        // Some other color constants/reservation
        [id: string]: HexString;
    };
};

export const config: PaletteConfig = {
    /** All color shades that are available
     * This colors are used as "key colors" to generate a tonal palette from 0 to 100
     * Steps are defined in 'tones'
     */
    baseColors: {
        green: {
            keyColor: "#7AC51B",
            tones: [98],
        },
        purple: {
            keyColor: "#661bc5",
            tones: [],
        },
        neutral: {
            keyColor: "#807788",
            tones: [2, 5, 8, 98],
        },
        red: {
            keyColor: "#e82439",
            tones: [95],
        },
        yellow: {
            keyColor: "#E0E01F",
            tones: [98],
        },
        blue: {
            keyColor: "#1B7AC5",
            tones: [95],
        },
    },

    /** Common tones to generate out of all the baseColors
     * number equals to the amount of light present in the color (HCT Color Space)
     */
    tones: [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],

    /** create aliases from the color palette
     *
     * @example
     *
     * primary: "blue"
     * ->
     * ...
     * primary40 -> blue40
     * primary50 -> blue50
     * ...
     */
    aliases: {
        primary: "purple",
        secondary: "green",
        error: "red",
    },
    /** some color names are reserved
     * typically those colors do not change when switching theme
     * or are other types of constant in the UI
     */
    common: {
        white: "#ffffff",
        black: "#000000",
    },
};
