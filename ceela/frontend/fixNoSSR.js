const fs = require("fs");
const path = require("path");

const folder = "./src/components"; // Cambia esto a la carpeta donde están los archivos

function processFiles(dir) {
  fs.readdirSync(dir).forEach((file) => {
    const fullPath = path.join(dir, file);

    if (fs.lstatSync(fullPath).isDirectory()) {
      processFiles(fullPath);
    } else if (file.endsWith(".tsx") || file.endsWith(".js")) {
      let content = fs.readFileSync(fullPath, "utf-8");

      if (content.includes("document") || content.includes("window")) {
        content = `import useIsClient from "../utils/useIsClient";\n${content}`;
        content = content.replace(
          /(document|window|localStorage)/g,
          "useIsClient() && $1"
        );

        fs.writeFileSync(fullPath, content, "utf-8");
        console.log(`✔ Modificado: ${fullPath}`);
      }
    }
  });
}

processFiles(folder);
