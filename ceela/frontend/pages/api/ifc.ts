import { promises as fs } from 'fs';
import path from 'path';
import formidable, { File } from 'formidable';
import type { NextApiRequest, NextApiResponse } from 'next';
import { spawn } from 'child_process';

let convert2xkt: any;
try {
    convert2xkt = (await import("@xeokit/xeokit-convert/dist/convert2xkt.cjs.js")).convert2xkt;
} catch (error) {
    console.error("Failed to import convert2xkt:", error);
}

export const config = {
    api: {
        bodyParser: false,
    },
};

type ProcessedFiles = Array<[string, File]>;

const handler = async (req: NextApiRequest, res: NextApiResponse) => {
    let status = 200,
        resultBody = { status: 'ok', message: 'Files were uploaded successfully' };

    const files = await new Promise<ProcessedFiles | undefined>((resolve, reject) => {
        const form = formidable({
            keepExtensions: true,
            multiples: true,
        });
        const files: ProcessedFiles = [];
        form.on('file', function (field: string, file: File) {
            files.push([field, file]);
        });
        form.on('end', () => resolve(files));
        form.on('error', err => reject(err));
        form.parse(req, () => {
            //
        });
    }).catch(e => {
        console.log(e);
        status = 500;
        resultBody = {
            status: 'fail', message: 'Upload error'
        };
    });

    if (files?.length && convert2xkt) {
        const targetPath = path.join(process.cwd(), `/uploads/`);
        const publicPath = path.join(process.cwd(), `/public/`);
        try {
            await fs.access(targetPath);
        } catch (e) {
            await fs.mkdir(targetPath);
        }
        try {
            await fs.access(publicPath);
        } catch (e) {
            await fs.mkdir(publicPath);
        }

        for (const file of files) {
            const tempPath = file[1].filepath;
            const newFilePath = path.join(targetPath, file[1].originalFilename as string);
            const outputFilePath = path.join(publicPath, `output.ifc.xkt`);
            await fs.rename(tempPath, newFilePath);
            try {
                const process = spawn("node", ["./node_modules/@xeokit/xeokit-convert/convert2xkt.js", "-s", newFilePath, "-o", outputFilePath, "-l"], {
                    stdio: "inherit",
                    detached: true,
                    shell: false,
                });

                process.on("close", (code) => {
                    console.log(`Proceso finalizado con código ${code}`);
                    if (code === 0) {
                        res.status(200).json({ status: 'ok', message: 'Files were uploaded and converted successfully' });
                    } else {
                        res.status(500).json({ status: 'fail', message: 'Conversion process failed' });
                    }
                });
                return; // Exit the loop and wait for the process to finish
            } catch (error) {
                console.error(`Error converting file ${file[1].originalFilename}:`, error);
                status = 500;
                resultBody = {
                    status: 'fail', message: 'Conversion error'
                };
            }
        }
    } else {
        status = 500;
        resultBody = {
            status: 'fail', message: 'Conversion error'
        };
    }

    res.status(200).json(resultBody); // Always return status 200
};

export default handler;
