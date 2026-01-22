import type { NextApiRequest, NextApiResponse } from "next";
import fs from "fs";
import path from "path";

const cssFilePath = path.join(process.cwd(), "public", "assets", "css", "globals.css");

const cssTemplate = `
@import url('https://fonts.googleapis.com/css2?family=Encode+Sans:wght@400;700&display=swap');

:root {
  --font-family-base: 'Encode Sans', sans-serif;
  --font-size-base: 16px;
  --font-size-heading: 2em;
  --primary-color: {primary_color};      /* Color principal, usado en títulos y botones */
  --secondary-color: {secondary_color};    /* Color secundario, por ejemplo para hover en botones */
  --background-color: {background_color};  /* Color de fondo */
  --text-color: #333;
  --muted-text: #d3d3d3;

  /* Variables para botones */
  --btn-save-bg: {btn_save_bg};
  --btn-save-hover-bg: {btn_save_hover_bg};
  --btn-back-bg: {btn_back_bg};
  --btn-back-hover-bg: {btn_back_hover_bg};
  --btn-delete-bg: {btn_delete_bg};
  --btn-delete-hover-bg: {btn_delete_hover_bg};
}

/* Estilos base */
body {
  font-family: var(--font-family-base);
  font-size: var(--font-size-base);
  color: var(--text-color);
  background-color: var(--background-color);
  margin: 0;
  padding: 0;
}
`;

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "PUT") {
    return res.status(405).json({ message: "Método no permitido" });
  }

  try {
    const {
      primary_color,
      secondary_color,
      background_color,
      btn_save_bg,
      btn_save_hover_bg,
      btn_back_bg,
      btn_back_hover_bg,
      btn_delete_bg,
      btn_delete_hover_bg,
    } = req.body;
    if (
      !primary_color ||
      !secondary_color ||
      !background_color ||
      !btn_save_bg ||
      !btn_save_hover_bg ||
      !btn_back_bg ||
      !btn_back_hover_bg ||
      !btn_delete_bg ||
      !btn_delete_hover_bg
    ) {
      return res.status(400).json({ message: "Faltan campos obligatorios" });
    }

    const newCss = cssTemplate
      .replace("{primary_color}", primary_color)
      .replace("{secondary_color}", secondary_color)
      .replace("{background_color}", background_color)
      .replace("{btn_save_bg}", btn_save_bg)
      .replace("{btn_save_hover_bg}", btn_save_hover_bg)
      .replace("{btn_back_bg}", btn_back_bg)
      .replace("{btn_back_hover_bg}", btn_back_hover_bg)
      .replace("{btn_delete_bg}", btn_delete_bg)
      .replace("{btn_delete_hover_bg}", btn_delete_hover_bg);

    fs.writeFileSync(cssFilePath, newCss, "utf8");

    return res.status(200).json({ message: "Archivo CSS actualizado exitosamente" });
  } catch (error) {
    console.error("Error al actualizar el CSS:", error);
    return res.status(500).json({ message: "Error al actualizar el CSS" });
  }
}
