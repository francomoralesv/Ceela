import { Html, Head, Main, NextScript } from "next/document";

export default function Document() {
  return (
    <Html lang="es">
      <Head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/assets/images/proyecto-deuman-logo.png" type="image/x-icon" />
        <link rel="shortcut icon" href="/assets/images/proyecto-deuman-logo.png" type="image/x-icon" />
        {/* Google Fonts */}
        <link
          href="https://fonts.googleapis.com/css?family=Outfit:400,400i,500,500i,700,700i&display=swap"
          rel="stylesheet"
        />
        <link
          href="https://fonts.googleapis.com/css?family=Roboto:300,300i,400,400i,500,500i,700,700i,900&display=swap"
          rel="stylesheet"
        />
      </Head>
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
