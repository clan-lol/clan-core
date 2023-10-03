import { writeFile } from "fs";
import palette from "./out.json" assert { type: "json" };
import { config } from "./config.js";

type PaletteFile = typeof palette;

const html = (palette: PaletteFile): string => {
    const colors = Object.keys(config.baseColors).map((baseName) => {
        const colors = Object.entries(palette.ref.palette)
            .filter(([name, _]) => name.includes(baseName))
            .sort((a, b) => {
                return a[1].meta.color.shade - b[1].meta.color.shade;
            })
            .map(([key, color]) => {
                console.log({ key, color });
                return `<div style="background-color:${color.value}; color:${
                    color.meta.color.shade < 48 ? "#fff" : "#000"
                }; height: 10rem; border:solid 1px grey; display:grid; place-items:end;">${key}</div>`;
            });
        return `<div style="display: grid; grid-template-columns: repeat(${13}, minmax(0, 1fr)); gap: 1rem; margin-bottom: 1rem">${colors.join(
            "\n",
        )}</div>`;
    });

    return `<!DOCTYPE html>
<html lang="en">
<meta charset="UTF-8">
<title>Page Title</title>
<style>
</style>
<body>

${colors.join("\n")}

</body>
</html>     
`;
};

writeFile("index.html", html(palette), (err) => {
    if (err) {
        console.error({ err });
    } else {
        console.log("Exported colors to html");
    }
});
