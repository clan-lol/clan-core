#!usr/bin/node
import * as fs from "fs";
import {
    argbFromHex,
    Hct,
    hexFromArgb,
} from "@material/material-color-utilities";
import {
    AliasTokenMap,
    ColorDesignToken,
    ColorSet,
    HexString,
    RefTokenSystem,
    TonalPalette,
    TonalPaletteConfig,
    TonalPaletteItem,
} from "./types.js";
import { config } from "./config.js";

const { baseColors, tones, aliases, common } = config;

/** Takes a color, tone and name
 * If a tone is given adjust the lightning level accordingly
 *
 * @returns TonalPaletteItem (meta wrapper around HCT)
 */
const getTonalPaletteItem = (
    value: HexString,
    name: string,
    tone?: number,
): TonalPaletteItem => {
    const aRGB = argbFromHex(value);
    const color = Hct.fromInt(aRGB);
    if (tone !== undefined) {
        color.tone = tone;
    }
    return {
        shade: color.tone,
        name: `${name || color.chroma}${Math.round(color.tone)}`,
        baseName: name,
        value: color,
    };
};

/** create a flat list of the cross product from all colors and all tones.
 *
 * every color is mapped in the range from 0 to 100
 * with the steps configure in `config.tones'
 * additionally the key color is added unmodified
 * lightning levels are rounded to the next natural number to form the 'name'
 * Example:
 *
 * "blue" x [20.1, 30.3]
 * ->
 * [blue20, blue30]
 */
const mkTonalPalette =
    (config: TonalPaletteConfig) =>
    (name: string) =>
    (keyTone: HexString): TonalPalette => {
        const { tones } = config;
        const aRGB = argbFromHex(keyTone);
        const HctColor = Hct.fromInt(aRGB);
        const roundedTone = Math.round(HctColor.tone * 100) / 100;

        const localTones = [...tones, roundedTone];

        return localTones.map((t) => getTonalPaletteItem(keyTone, name, t));
    };

/**
 * Converts a PaletteItem into a hex color. (Wrapped)
 * Adding meta attributes which avoids any information loss.
 */
const toDesignTokenContent = (color: TonalPaletteItem): ColorDesignToken => {
    const { value } = color;
    return {
        type: "color",
        value: hexFromArgb(value.toInt()),
        meta: {
            color,
            date: new Date(),
        },
    };
};

const color: ColorSet = Object.entries(baseColors)
    .map(([name, baseColor]) => ({
        name,
        baseColor,
        tones: mkTonalPalette({
            tones: [...tones, ...baseColor.tones].sort((a, b) => a - b),
        })(name)(baseColor.keyColor),
    }))
    .reduce((acc, curr) => {
        let currTones = curr.tones.reduce(
            (o, v) => ({
                ...o,
                [v.name]: toDesignTokenContent(v),
            }),
            {},
        );
        return {
            ...acc,
            ...currTones,
        };
    }, {});

/** Generate a set of tokens from a given alias mapping
 *
 * @param alias A string e.g. Primary -> Blue (Primary is the alias)
 * @param name A string; Basename of the referenced value (e.g. Blue)
 * @param colors A set of colors
 * @returns All aliases from the given color set
 */
function resolveAlias(
    alias: string,
    name: string,
    colors: ColorSet,
): AliasTokenMap {
    // All colors from the color map belonging to that single alias
    // Example:
    // Primary -> "blue"
    // =>
    // [ (blue0) , (blue10) , ...,  (blue100) ]
    const all = Object.values(colors)
        .filter((n) => n.meta.color.name.includes(name))
        .filter((n) => !n.meta.color.name.includes("."));

    const tokens = all
        .map((shade) => {
            const shadeNumber = shade.meta.color.shade;
            return {
                name: `${alias}${Math.round(shadeNumber)}`,
                value: { value: `{ref.palette.${shade.meta.color.name}}` },
                // propagate the meta attribute of the actual value
                meta: shade.meta,
            };
        })
        // sort by tone
        .sort((a, b) => a.meta.color.value.tone - b.meta.color.value.tone)
        .reduce((acc, { name, value }) => ({ ...acc, [name]: value }), {});
    return tokens;
}

const aliasMap = Object.entries(aliases).reduce(
    (prev, [key, value]) => ({
        ...prev,
        ...resolveAlias(key, value, color),
    }),
    {},
);

const commonColors = Object.entries(common)
    .map(([name, value]) =>
        toDesignTokenContent(getTonalPaletteItem(value, name)),
    )
    .reduce(
        (acc, val) => ({ ...acc, [val.meta.color.baseName]: val }),
        {},
    ) as ColorSet;

const toPaletteToken = (color: ColorSet): RefTokenSystem => ({
    ref: {
        palette: color,
        alias: aliasMap,
        common: commonColors,
    },
});

// Dump tokens to json file
fs.writeFile(
    "colors.json",
    JSON.stringify(toPaletteToken(color), null, 2),
    (err) => {
        if (err) {
            console.error({ err });
        } else {
            console.log("tokens successfully exported");
        }
    },
);
