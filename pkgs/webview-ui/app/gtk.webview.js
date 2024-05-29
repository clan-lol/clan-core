const fs = require("fs");
const path = require("path");

const distPath = path.resolve(__dirname, "dist");
const manifestPath = path.join(distPath, ".vite/manifest.json");
const outputPath = path.join(distPath, "index.html");

fs.readFile(manifestPath, { encoding: "utf8" }, (err, data) => {
  if (err) {
    return console.error("Failed to read manifest:", err);
  }

  const manifest = JSON.parse(data);
  /** @type {{    file: string;    name: string;    src: string;    isEntry: bool;    css: string[];  } []} */
  const assets = Object.values(manifest);

  console.log(`Generate custom index.html from ${manifestPath} ...`);
  // Start with a basic HTML structure
  let htmlContent = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Webview UI</title>`;

  // Add linked stylesheets
  assets.forEach((asset) => {
    console.log(asset);
    if (asset.src === "index.html") {
      asset.css.forEach((cssEntry) => {
        htmlContent += `\n    <link rel="stylesheet" href="${cssEntry}">`;
      });
    }
  });

  htmlContent += `
</head>
<body>
    <div id="app"></div>
`;
  // Add scripts
  assets.forEach((asset) => {
    if (asset.file.endsWith(".js")) {
      htmlContent += `\n    <script src="${asset.file}"></script>`;
    }
  });

  htmlContent += `
</body>
</html>`;

  // Write the HTML file
  fs.writeFile(outputPath, htmlContent, (err) => {
    if (err) {
      console.error("Failed to write custom index.html:", err);
    } else {
      console.log("Custom index.html generated successfully!");
    }
  });
});
