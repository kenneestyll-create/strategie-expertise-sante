/**
 * Document processing pipeline using OpenCV.js
 * Capture → Detect edges → Perspective warp → Enhance
 */

/* ── Helper: order 4 points as [TL, TR, BR, BL] ── */
function orderPoints(pts) {
  // pts = [{x, y}, ...]
  const sorted = [...pts];
  // Sum-based: TL has smallest sum, BR has largest
  sorted.sort((a, b) => (a.x + a.y) - (b.x + b.y));
  const tl = sorted[0];
  const br = sorted[3];
  // Diff-based: TR has smallest diff(y-x), BL has largest
  sorted.sort((a, b) => (a.y - a.x) - (b.y - b.x));
  const tr = sorted[0];
  const bl = sorted[3];
  return [tl, tr, br, bl];
}

function distance(p1, p2) {
  return Math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2);
}

/**
 * Detect document edges and return 4 corner points
 * Returns null if no document found
 */
export function detectDocument(cv, srcMat) {
  const gray = new cv.Mat();
  const blurred = new cv.Mat();
  const edges = new cv.Mat();

  try {
    // Grayscale
    cv.cvtColor(srcMat, gray, cv.COLOR_RGBA2GRAY);

    // Gaussian blur to reduce noise
    cv.GaussianBlur(gray, blurred, new cv.Size(5, 5), 0);

    // Canny edge detection — multiple thresholds for robustness
    const thresholds = [
      [50, 150],
      [30, 100],
      [75, 200],
    ];

    for (const [low, high] of thresholds) {
      cv.Canny(blurred, edges, low, high);

      // Dilate to close gaps in edges
      const kernel = cv.getStructuringElement(cv.MORPH_RECT, new cv.Size(3, 3));
      cv.dilate(edges, edges, kernel);
      kernel.delete();

      // Find contours
      const contours = new cv.MatVector();
      const hierarchy = new cv.Mat();
      cv.findContours(edges, contours, hierarchy, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE);

      // Find largest quadrilateral
      const imgArea = srcMat.rows * srcMat.cols;
      let bestCorners = null;
      let bestArea = 0;

      for (let i = 0; i < contours.size(); i++) {
        const contour = contours.get(i);
        const area = cv.contourArea(contour);

        // Document should be at least 10% of image area
        if (area < imgArea * 0.1) continue;

        const peri = cv.arcLength(contour, true);
        const approx = new cv.Mat();
        cv.approxPolyDP(contour, approx, 0.02 * peri, true);

        if (approx.rows === 4 && area > bestArea) {
          // Extract corner points
          const points = [];
          for (let j = 0; j < 4; j++) {
            points.push({
              x: approx.data32S[j * 2],
              y: approx.data32S[j * 2 + 1],
            });
          }
          bestCorners = orderPoints(points);
          bestArea = area;
        }
        approx.delete();
      }

      contours.delete();
      hierarchy.delete();

      if (bestCorners) return bestCorners;
    }

    return null;
  } finally {
    gray.delete();
    blurred.delete();
    edges.delete();
  }
}

/**
 * Apply perspective warp to straighten the document
 */
export function warpDocument(cv, srcMat, corners) {
  const [tl, tr, br, bl] = corners;

  // Compute output dimensions
  const widthTop = distance(tl, tr);
  const widthBot = distance(bl, br);
  const maxW = Math.round(Math.max(widthTop, widthBot));

  const heightLeft = distance(tl, bl);
  const heightRight = distance(tr, br);
  const maxH = Math.round(Math.max(heightLeft, heightRight));

  // Source points
  const srcPts = cv.matFromArray(4, 1, cv.CV_32FC2, [
    tl.x, tl.y, tr.x, tr.y, br.x, br.y, bl.x, bl.y,
  ]);

  // Destination points
  const dstPts = cv.matFromArray(4, 1, cv.CV_32FC2, [
    0, 0, maxW, 0, maxW, maxH, 0, maxH,
  ]);

  const M = cv.getPerspectiveTransform(srcPts, dstPts);
  const warped = new cv.Mat();
  cv.warpPerspective(srcMat, warped, M, new cv.Size(maxW, maxH));

  srcPts.delete();
  dstPts.delete();
  M.delete();

  return warped;
}

/**
 * Enhance document image — clean mode without black artifacts
 */
export function enhanceDocument(cv, srcMat, mode = 'document') {
  const result = new cv.Mat();

  if (mode === 'original') {
    srcMat.copyTo(result);
    return result;
  }

  const gray = new cv.Mat();

  // Convert to grayscale if needed
  if (srcMat.channels() === 4) {
    cv.cvtColor(srcMat, gray, cv.COLOR_RGBA2GRAY);
  } else if (srcMat.channels() === 3) {
    cv.cvtColor(srcMat, gray, cv.COLOR_RGB2GRAY);
  } else {
    srcMat.copyTo(gray);
  }

  if (mode === 'bw') {
    // Adaptive threshold — clean B&W like CamScanner
    // First, remove shadows with morphological opening
    const morphed = new cv.Mat();
    const kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, new cv.Size(21, 21));
    cv.morphologyEx(gray, morphed, cv.MORPH_CLOSE, kernel);

    // Divide gray by morphed to normalize lighting
    const normalized = new cv.Mat();
    cv.divide(gray, morphed, normalized, 255.0);

    // Adaptive threshold for clean binarization
    cv.adaptiveThreshold(
      normalized, result,
      255,
      cv.ADAPTIVE_THRESH_GAUSSIAN_C,
      cv.THRESH_BINARY,
      21,  // Block size
      10   // C constant — higher = more white, avoids black spots
    );

    morphed.delete();
    kernel.delete();
    normalized.delete();
  } else {
    // 'document' mode — enhanced contrast + sharpening, no binarization
    // Shadow removal via morphological normalization
    const morphed = new cv.Mat();
    const kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, new cv.Size(25, 25));
    cv.morphologyEx(gray, morphed, cv.MORPH_CLOSE, kernel);

    const normalized = new cv.Mat();
    cv.divide(gray, morphed, normalized, 255.0);

    // Contrast stretch
    const minMax = cv.minMaxLoc(normalized);
    const alpha = 255.0 / Math.max(1, minMax.maxVal - minMax.minVal);
    const beta = -minMax.minVal * alpha;
    normalized.convertTo(result, -1, alpha * 1.3, beta + 10);

    // Sharpening via unsharp mask
    const blurred = new cv.Mat();
    cv.GaussianBlur(result, blurred, new cv.Size(0, 0), 2.0);
    cv.addWeighted(result, 1.5, blurred, -0.5, 0, result);

    morphed.delete();
    kernel.delete();
    normalized.delete();
    blurred.delete();
  }

  gray.delete();
  return result;
}

/**
 * Full pipeline: detect → warp → enhance
 * Returns { resultDataUrl, corners, autoDetected }
 */
export function processDocument(cv, imageDataUrl, enhanceMode = 'document') {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      // Load into OpenCV Mat
      const canvas = document.createElement('canvas');
      canvas.width = img.width;
      canvas.height = img.height;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0);
      const src = cv.imread(canvas);

      let processed;
      let corners = null;
      let autoDetected = false;

      // Try auto-detection
      try {
        corners = detectDocument(cv, src);
      } catch (e) {
        console.warn('Edge detection failed:', e);
      }

      if (corners) {
        // Warp + enhance
        autoDetected = true;
        const warped = warpDocument(cv, src, corners);
        processed = enhanceDocument(cv, warped, enhanceMode);
        warped.delete();
      } else {
        // No document found — enhance original
        processed = enhanceDocument(cv, src, enhanceMode);
      }

      // Convert result to data URL
      const outCanvas = document.createElement('canvas');
      cv.imshow(outCanvas, processed);
      const resultDataUrl = outCanvas.toDataURL('image/jpeg', 0.92);

      // Cleanup
      src.delete();
      processed.delete();

      resolve({ resultDataUrl, corners, autoDetected });
    };
    img.src = imageDataUrl;
  });
}

/**
 * Re-process with manual corners (for fallback adjustment)
 */
export function reprocessWithCorners(cv, imageDataUrl, corners, enhanceMode = 'document') {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement('canvas');
      canvas.width = img.width;
      canvas.height = img.height;
      canvas.getContext('2d').drawImage(img, 0, 0);
      const src = cv.imread(canvas);

      const warped = warpDocument(cv, src, corners);
      const processed = enhanceDocument(cv, warped, enhanceMode);

      const outCanvas = document.createElement('canvas');
      cv.imshow(outCanvas, processed);
      const resultDataUrl = outCanvas.toDataURL('image/jpeg', 0.92);

      src.delete();
      warped.delete();
      processed.delete();

      resolve(resultDataUrl);
    };
    img.src = imageDataUrl;
  });
}
