const COUNTER_KEY = "github-profile-visits";

export default {
  async fetch(request, env) {
    if (request.method !== "GET") {
      return new Response("Method Not Allowed", {
        status: 405,
        headers: { allow: "GET" },
      });
    }

    const url = new URL(request.url);
    if (url.pathname !== "/" && url.pathname !== "/visitor.svg") {
      return new Response("Not Found", { status: 404 });
    }

    if (!env.VISITOR_COUNTER) {
      return new Response("Missing KV binding: VISITOR_COUNTER", { status: 500 });
    }

    const currentValue = await env.VISITOR_COUNTER.get(COUNTER_KEY);
    const nextCount = (Number.parseInt(currentValue ?? "0", 10) || 0) + 1;
    await env.VISITOR_COUNTER.put(COUNTER_KEY, String(nextCount));

    return new Response(renderSvg(nextCount), {
      headers: {
        "content-type": "image/svg+xml; charset=utf-8",
        "cache-control": "no-store, no-cache, max-age=0, must-revalidate",
      },
    });
  },
};

function renderSvg(count) {
  const paddedCount = String(count).padStart(7, "0");

  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="750" height="45" viewBox="0 0 750 45" role="img" aria-labelledby="title desc">
  <title id="title">💮 ~ あなたは ${paddedCount} 人目の訪問者です。 ~ 💮</title>
  <desc id="desc">GitHub profile visitor counter.</desc>
  <defs>
    <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#ffb7c5" />
      <stop offset="100%" stop-color="#c9f0ff" />
    </linearGradient>
  </defs>

  <rect width="750" height="45" rx="12" fill="#ffffff" stroke="#f0e8e0" stroke-width="1" />

  <rect x="0" y="0" width="750" height="4" rx="2" fill="url(#accent)" />

  <circle cx="30" cy="23" r="8" fill="#ffb7c5" opacity="0.5" />
  <circle cx="720" cy="23" r="8" fill="#c9f0ff" opacity="0.5" />

  <text x="375" y="26" text-anchor="middle" dominant-baseline="central">
    <tspan class="text">💮 ~ あなたは</tspan>
    <tspan class="count" dx="1">${escapeXml(paddedCount)}</tspan>
    <tspan class="text" dx="1">人目の訪問者です。 ~ 💮</tspan>
  </text>

  <style>
    .text {
      fill: #7a5a4a;
      font-family: "Yuji Syuku", "Hiragino Maru Gothic ProN", "Segoe Print", cursive;
      font-size: 22px;
      font-weight: 600;
    }
    .count {
      fill: #d45a7a;
      font-family: "Yuji Syuku", "Hiragino Maru Gothic ProN", "Segoe Print", cursive;
      font-size: 26px;
      font-weight: 700;
    }
  </style>
</svg>`;
}

function escapeXml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&apos;");
}
