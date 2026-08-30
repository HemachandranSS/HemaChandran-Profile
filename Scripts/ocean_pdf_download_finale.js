// ======================================================
// INSTALL
// ======================================================
//
// npm install playwright
// npx playwright install chromium
//
// RUN
// ======================================================
//
// node download_oceanofpdf.js
//
// ======================================================

const { chromium } = require("playwright");
const path = require("path");
const fs = require("fs");

// ======================================================
// SETTINGS
// ======================================================

const START_PAGE = 1;
const END_PAGE = 1304;

const SEARCH_TERM = "in+action";

const DOWNLOAD_DIR =
  "/home/cipl1168/Downloads/In_Action_Manning";
//const DOWNLOAD_DIR =
//  "/media/cipl1168/One Touch1/Pdf Books/Shashi_Tharoor";

// 5 minutes for manual CAPTCHA completion
const DOWNLOAD_TIMEOUT = 300000;

// ======================================================
// CREATE DOWNLOAD DIRECTORY
// ======================================================

if (!fs.existsSync(DOWNLOAD_DIR)) {
  fs.mkdirSync(
    DOWNLOAD_DIR,
    {
      recursive: true,
    }
  );
}

// ======================================================
// CLEAN FILE NAME
// ======================================================

function sanitizeFilename(
  filename
) {
  return filename
    .replace(
      /[<>:"/\\|?*\x00-\x1F]/g,
      "_"
    )
    .trim();
}

// ======================================================
// FORMAT FILE SIZE
// ======================================================

function formatFileSize(
  bytes
) {
  return (
    bytes /
    1024 /
    1024
  ).toFixed(2);
}

// ======================================================
// MAIN
// ======================================================

(async () => {
  let browser;

  try {
    // ==================================================
    // START CHROMIUM
    // ==================================================

    browser =
      await chromium.launch({
        headless: false,

        slowMo: 300,

        args: [
          "--disable-blink-features=AutomationControlled",
          "--start-maximized",
        ],
      });

    // ==================================================
    // CREATE BROWSER CONTEXT
    // ==================================================

    const context =
      await browser.newContext({
        viewport: null,

        // Required for native downloads
        acceptDownloads: true,
      });

    // ==================================================
    // HIDE WEBDRIVER
    // ==================================================

    await context.addInitScript(
      () => {
        Object.defineProperty(
          navigator,
          "webdriver",
          {
            get: () =>
              undefined,
          }
        );
      }
    );

    // ==================================================
    // DOWNLOAD DIRECTORY
    // ==================================================

    console.log(
      `Download folder: ${DOWNLOAD_DIR}`
    );

    // ==================================================
    // CATEGORY PAGE
    // ==================================================

    const categoryPage =
      await context.newPage();

    // ==================================================
    // CATEGORY LOOP
    // ==================================================

    for (
      let pageNumber =
        START_PAGE;

      pageNumber <=
        END_PAGE;

      pageNumber++
    ) {
      const categoryUrl =
        `https://oceanofpdf.com/` +
        `page/${pageNumber}/` +
        `?s=${encodeURIComponent(
          SEARCH_TERM
        )}`;
	
      console.log(
        "\n========================================"
      );

      console.log(
        `CATEGORY PAGE ${pageNumber}`
      );

      console.log(
        categoryUrl
      );

      console.log(
        "========================================"
      );

      try {
        // ==============================================
        // OPEN CATEGORY PAGE
        // ==============================================

        await categoryPage.goto(
          categoryUrl,
          {
            waitUntil:
              "domcontentloaded",

            timeout: 60000,
          }
        );

	if(START_PAGE == pageNumber){
        await categoryPage
          .waitForTimeout(
            6000
          );
         }
         else{
         await categoryPage
          .waitForTimeout(
            3000
          );
         }
          

        // ==============================================
        // GET ARTICLE LINKS
        // ==============================================

        const articleLinks =
          await categoryPage.$$eval(
            "a.entry-image-link",

            (links) => [
              ...new Set(
                links
                  .map(
                    (link) =>
                      link.href
                  )
                  .filter(
                    Boolean
                  )
              ),
            ]
          );

        console.log(
          `Found ` +
          `${articleLinks.length} ` +
          `articles`
        );

        // ==============================================
        // ARTICLE LOOP
        // ==============================================

        for (
          const articleUrl
          of articleLinks
        ) {
          let articlePage;

          console.log(
            "\n----------------------------------------"
          );

          console.log(
            "ARTICLE"
          );

          console.log(
            articleUrl
          );

          console.log(
            "----------------------------------------"
          );

          try {
            // ==========================================
            // OPEN ARTICLE
            // ==========================================

            articlePage =
              await context.newPage();

            await articlePage.goto(
              articleUrl,
              {
                waitUntil:
                  "domcontentloaded",

                timeout: 60000,
              }
            );

            await articlePage
              .waitForTimeout(
                3000
              );

            // ==========================================
            // FIND PDF INPUTS
            // ==========================================

            const pdfInputs =
              await articlePage.$$(
                'form[action*=' +
                '"Fetching_Resource.php"] ' +
                'input[name="filename"]' +
                '[value$=".pdf"]'
              );

            console.log(
              `Found ` +
              `${pdfInputs.length} ` +
              `PDF forms`
            );

            if (
              pdfInputs.length ===
              0
            ) {
              continue;
            }

            // ==========================================
            // PDF LOOP
            // ==========================================

            for (
              let pdfIndex = 0;

              pdfIndex <
                pdfInputs.length;

              pdfIndex++
            ) {
              let downloadPage;

              try {
                // ======================================
                // GET PDF FILE NAME
                // ======================================

                const originalFilename =
                  await pdfInputs[
                    pdfIndex
                  ].getAttribute(
                    "value"
                  );

                if (
                  !originalFilename
                ) {
                  console.log(
                    "Missing PDF filename"
                  );

                  continue;
                }

                const filename =
                  sanitizeFilename(
                    originalFilename
                  );

                const savePath =
                  path.join(
                    DOWNLOAD_DIR,
                    filename
                  );

                console.log(
                  `\nPDF: ${filename}`
                );

                // ======================================
                // SKIP EXISTING FILE
                // ======================================

                if (
                  fs.existsSync(
                    savePath
                  )
                ) {
                  const existingSize =
                    fs.statSync(
                      savePath
                    ).size;

                  if (
                    existingSize >
                    0
                  ) {
                    console.log(
                      "Already downloaded. " +
                      "Skipping..."
                    );

                    continue;
                  }

                  // Delete empty file
                  fs.unlinkSync(
                    savePath
                  );
                }

                // ======================================
                // GET PARENT FORM
                // ======================================

                const formHandle =
                  await pdfInputs[
                    pdfIndex
                  ].evaluateHandle(
                    (input) =>
                      input.closest(
                        "form"
                      )
                  );

                // ======================================
                // REGISTER EVENTS BEFORE SUBMISSION
                // ======================================

                const newPagePromise =
                  context.waitForEvent(
                    "page",
                    {
                      timeout:
                        DOWNLOAD_TIMEOUT,
                    }
                  );

                const downloadPromise =
                  context.waitForEvent(
                    "download",
                    {
                      timeout:
                        DOWNLOAD_TIMEOUT,
                    }
                  );

                // ======================================
                // SUBMIT FORM
                // ======================================

                console.log(
                  "Submitting PDF form..."
                );

                await formHandle
                  .evaluate(
                    (form) => {
                      form.submit();
                    }
                  );

                // ======================================
                // GET NEW DOWNLOAD PAGE
                // ======================================

                downloadPage =
                  await newPagePromise;

                console.log(
                  "\nDownload page opened"
                );

                console.log(
                  "If CAPTCHA appears, " +
                  "solve it manually..."
                );

                console.log(
                  "Waiting for browser download..."
                );

                // ======================================
                // WAIT FOR NATIVE DOWNLOAD
                // ======================================

                const download =
                  await downloadPromise;

                console.log(
                  "\nDownload detected"
                );

                console.log(
                  `Browser filename: ` +
                  `${download.suggestedFilename()}`
                );

                // ======================================
                // CHECK DOWNLOAD FAILURE
                // ======================================

                const failure =
                  await download.failure();

                if (
                  failure
                ) {
                  throw new Error(
                    `Browser download failed: ` +
                    `${failure}`
                  );
                }

                // ======================================
                // SAVE DOWNLOAD
                // ======================================

                console.log(
                  "Saving PDF..."
                );

                await download.saveAs(
                  savePath
                );

                // ======================================
                // VERIFY FILE
                // ======================================

                if (
                  !fs.existsSync(
                    savePath
                  )
                ) {
                  throw new Error(
                    "PDF file was not created"
                  );
                }

                const fileSize =
                  fs.statSync(
                    savePath
                  ).size;

                if (
                  fileSize ===
                  0
                ) {
                  fs.unlinkSync(
                    savePath
                  );

                  throw new Error(
                    "Downloaded PDF is empty"
                  );
                }

                // ======================================
                // VERIFY PDF SIGNATURE
                // ======================================

                const fileDescriptor =
                  fs.openSync(
                    savePath,
                    "r"
                  );

                const signatureBuffer =
                  Buffer.alloc(
                    5
                  );

                fs.readSync(
                  fileDescriptor,
                  signatureBuffer,
                  0,
                  5,
                  0
                );

                fs.closeSync(
                  fileDescriptor
                );

                const signature =
                  signatureBuffer
                    .toString();

                if (
                  signature !==
                  "%PDF-"
                ) {
                  fs.unlinkSync(
                    savePath
                  );

                  throw new Error(
                    "Downloaded file " +
                    "is not a valid PDF"
                  );
                }

                // ======================================
                // SUCCESS
                // ======================================

                console.log(
                  `\nSaved: ${savePath}`
                );

                console.log(
                  `File size: ` +
                  `${formatFileSize(
                    fileSize
                  )} MB`
                );

                console.log(
                  "PDF download completed"
                );
              } catch (
                formError
              ) {
                console.log(
                  "\nForm error:"
                );

                console.log(
                  formError.message
                );
              } finally {
                // ======================================
                // CLOSE DOWNLOAD PAGE
                // ======================================

                if (
                  downloadPage &&
                  !downloadPage
                    .isClosed()
                ) {
                  try {
                    await downloadPage
                      .close();

                    console.log(
                      "Closed download tab"
                    );
                  } catch {}
                }
              }
            }
          } catch (
            articleError
          ) {
            console.log(
              "\nArticle error:"
            );

            console.log(
              articleError.message
            );
          } finally {
            // ==========================================
            // CLOSE ARTICLE PAGE
            // ==========================================

            if (
              articlePage &&
              !articlePage
                .isClosed()
            ) {
              try {
                await articlePage
                  .close();
              } catch {}
            }
          }
        }
      } catch (
        categoryError
      ) {
        console.log(
          "\nCategory error:"
        );

        console.log(
          categoryError.message
        );
      }
    }

    // ==================================================
    // COMPLETED
    // ==================================================

    console.log(
      "\n========================================"
    );

    console.log(
      "ALL DOWNLOADS COMPLETED"
    );

    console.log(
      "========================================"
    );
  } catch (
    mainError
  ) {
    console.error(
      "\nFatal error:"
    );

    console.error(
      mainError.message
    );
  } finally {
    // ==================================================
    // CLOSE BROWSER
    // ==================================================

    if (
      browser
    ) {
      await browser.close();
    }
  }
})();
