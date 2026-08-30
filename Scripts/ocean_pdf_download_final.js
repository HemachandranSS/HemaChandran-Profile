// ======================================================
// INSTALL
// ======================================================
//
// npm install playwright axios
// npx playwright install chromium
//
// RUN
// ======================================================
//
// node download_oceanofpdf.js
//
// ======================================================

const { chromium } = require("playwright");
const axios = require("axios");
const path = require("path");
const fs = require("fs");

// ======================================================
// SETTINGS
// ======================================================

const START_PAGE = 1;
const END_PAGE = 13;

// ======================================================
// DOWNLOAD FILE
// ======================================================

async function downloadFile(url, outputPath) {
  const response = await axios({
    method: "GET",
    url,
    responseType: "stream",
  });

  const writer = fs.createWriteStream(outputPath);

  response.data.pipe(writer);

  return new Promise((resolve, reject) => {
    writer.on("finish", resolve);
    writer.on("error", reject);
  });
}

// ======================================================

(async () => {
  const browser = await chromium.launch({
    headless: false,

    slowMo: 300,

    args: [
      "--disable-blink-features=AutomationControlled",
      "--start-maximized",
    ],
  });

  const context = await browser.newContext({
    viewport: null,
  });

  // ======================================================
  // HIDE WEBDRIVER
  // ======================================================

  await context.addInitScript(() => {
    Object.defineProperty(navigator, "webdriver", {
      get: () => undefined,
    });
  });

  // ======================================================
  // DOWNLOAD DIRECTORY
  // ======================================================

  //const downloadDir = path.join(__dirname, "/media/cipl1168/PRAVEEN-USB/PDFs/Business");
  const downloadDir = "/home/cipl1168/Downloads/Devops";

  if (!fs.existsSync(downloadDir)) {
    fs.mkdirSync(downloadDir);
  }

  console.log(`Download folder: ${downloadDir}`);

  // ======================================================

  const page = await context.newPage();

  // ======================================================
  // CATEGORY LOOP
  // ======================================================

  for (let i = START_PAGE; i <= END_PAGE; i++) {
    const categoryUrl =
      i === 1
        ? `https://oceanofpdf.com/page/${i}/?s=Devops`
        : `https://oceanofpdf.com/page/${i}/?s=Devops`;

    console.log("\n================================================");
    console.log(`CATEGORY PAGE ${i}`);
    console.log(categoryUrl);
    console.log("================================================");

    try {
      await page.goto(categoryUrl, {
        waitUntil: "domcontentloaded",
        timeout: 60000,
      });

      await page.waitForTimeout(3000);

      // ======================================================
      // GET ARTICLE LINKS
      // ======================================================

      const articleLinks = await page.$$eval(
        "a.entry-image-link",
        (links) => [...new Set(links.map((a) => a.href))]
      );

      console.log(`Found ${articleLinks.length} articles`);

      // ======================================================
      // ARTICLE LOOP
      // ======================================================

      for (const articleUrl of articleLinks) {
        console.log("\n------------------------------------------------");
        console.log(`ARTICLE`);
        console.log(articleUrl);
        console.log("------------------------------------------------");

        let articlePage;

        try {
          articlePage = await context.newPage();

          await articlePage.goto(articleUrl, {
            waitUntil: "domcontentloaded",
            timeout: 60000,
          });

          await articlePage.waitForTimeout(3000);

          // ======================================================
          // FIND PDF FORMS
          // ======================================================

          const pdfInputs = await articlePage.$$(
            'form[action*="Fetching_Resource.php"] input[name="filename"][value$=".pdf"]'
          );

          console.log(
            `Found ${pdfInputs.length} PDF forms`
          );

          if (pdfInputs.length === 0) {
            await articlePage.close();
            continue;
          }

          // ======================================================
          // PDF LOOP
          // ======================================================

          for (let j = 0; j < pdfInputs.length; j++) {
            try {
              // ======================================================
              // GET PDF FILENAME
              // ======================================================

              const filename =
                await pdfInputs[j].getAttribute(
                  "value"
                );

              console.log(`\nPDF: ${filename}`);

              // ======================================================
              // GET FORM
              // ======================================================

              const formHandle =
                await pdfInputs[j].evaluateHandle((input) =>
                  input.closest("form")
                );

              // ======================================================
              // WAIT FOR NEW TAB
              // ======================================================

              const newPagePromise =
                context.waitForEvent("page");

              // ======================================================
              // SUBMIT FORM
              // ======================================================

              await formHandle.evaluate((form) => {
                form.submit();
              });

              // ======================================================
              // GET NEW TAB
              // ======================================================

              const newPage = await newPagePromise;

              await newPage.waitForLoadState();

              console.log(
                "\nIf captcha appears solve manually..."
              );

              console.log(
                "Waiting automatically for PDF network request..."
              );

              // ======================================================
              // WAIT FOR PDF RESPONSE
              // ======================================================

              const response =
                await newPage.waitForResponse(
                  async (response) => {
                    const url = response.url();

                    const contentType =
                      response.headers()[
                        "content-type"
                      ] || "";

                    return (
                      (
                        url.includes(".pdf") ||
                        contentType.includes("pdf")
                      ) &&
                      response.status() === 200
                    );
                  },
                  {
                    timeout: 300000,
                  }
                );

              // ======================================================
              // PDF URL
              // ======================================================

              const pdfUrl = response.url();

              console.log("\nPDF URL FOUND:");
              console.log(pdfUrl);

              // ======================================================
              // SAVE PATH
              // ======================================================

              const savePath = path.join(
                downloadDir,
                filename
              );

              // ======================================================
              // DOWNLOAD PDF
              // ======================================================

              console.log("\nDownloading PDF...");

              await downloadFile(pdfUrl, savePath);

              console.log(`Saved: ${savePath}`);

              // ======================================================
              // CLOSE TAB
              // ======================================================

              await newPage.close();

              console.log("Closed download tab");
            } catch (formError) {
              console.log(
                `Form error: ${formError.message}`
              );
            }
          }

          await articlePage.close();
        } catch (articleError) {
          console.log(
            `Article error: ${articleError.message}`
          );

          if (articlePage) {
            try {
              await articlePage.close();
            } catch {}
          }
        }
      }
    } catch (categoryError) {
      console.log(
        `Category error: ${categoryError.message}`
      );
    }
  }

  console.log("\n====================================");
  console.log("DONE");
  console.log("====================================");

  await browser.close();
})();
