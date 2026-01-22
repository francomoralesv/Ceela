import type { NextApiRequest, NextApiResponse } from "next";
import formidable from "formidable";
import fs from "fs";
import path from "path";

export const config = {
  api: {
    bodyParser: false,
  },
};

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "POST") {
    return res.status(405).json({ message: "Método no permitido" });
  }

  const uploadDir = path.join(process.cwd(), "public", "assets", "images");

  // Asegurarse de que el directorio exista
  if (!fs.existsSync(uploadDir)) {
    fs.mkdirSync(uploadDir, { recursive: true });
  }

  const form = new formidable.IncomingForm({ uploadDir, keepExtensions: true });

  form.parse(req, (err, _fields, files) => {
    if (err) {
      console.error("Error al parsear la carga:", err);
      return res.status(500).json({ message: "Error al subir el logo" });
    }

    const file = files.logo;
    if (!file) {
      return res.status(400).json({ message: "No se subió ningún archivo" });
    }

    const fileData = Array.isArray(file) ? file[0] : file;
    const fileName = path.basename(fileData.filepath);
    const logoUrl = `/assets/images/${fileName}`;
    return res.status(200).json({ logoUrl });
  });
}
