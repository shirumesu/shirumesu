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
  <title id="title">✿ あなたは ${paddedCount} 人目の訪問者です。 ✿</title>
  <desc id="desc">GitHub profile visitor counter - notebook style.</desc>
  <defs>
    <pattern id="dots" x="0" y="0" width="15" height="15" patternUnits="userSpaceOnUse">
      <circle cx="1" cy="1" r="0.8" fill="#ffc9e0" opacity="0.15" />
    </pattern>
    <filter id="paper">
      <feTurbulence type="fractalNoise" baseFrequency="0.04" numOctaves="2" result="noise" />
      <feDiffuseLighting in="noise" lighting-color="#fff" surfaceScale="1" result="light">
        <feDistantLight azimuth="45" elevation="35" />
      </feDiffuseLighting>
      <feComposite in="SourceGraphic" in2="light" operator="arithmetic" k1="1" k2="0" k3="0" k4="0" />
    </filter>
  </defs>

  <!-- 纸张背景 -->
  <rect width="750" height="45" rx="10" fill="#fffbf5" />
  <rect width="750" height="45" rx="10" fill="url(#dots)" />
  
  <!-- 手绘边框 -->
  <path d="M 10 2 Q 375 3 740 2 L 748 23 Q 748 35 740 43 L 10 43 Q 2 43 2 35 L 2 10 Q 2 2 10 2 Z" 
        fill="none" stroke="#ffb7d5" stroke-width="1.5" stroke-linecap="round" opacity="0.6" />
  
  <!-- 顶部虚线装饰 -->
  <line x1="10" y1="8" x2="740" y2="8" stroke="#ffc9e0" stroke-width="1" stroke-dasharray="4,4" opacity="0.5" />
  
  <!-- 底部波浪线 -->
  <path d="M 10 37 Q 30 35 50 37 T 90 37 T 130 37 T 170 37 T 210 37 T 250 37 T 290 37 T 330 37 T 370 37 T 410 37 T 450 37 T 490 37 T 530 37 T 570 37 T 610 37 T 650 37 T 690 37 T 730 37 L 740 37" 
        stroke="#ffb7d5" stroke-width="1" fill="none" opacity="0.4" />

  <!-- 左侧手绘樱花 -->
  <g opacity="0.7">
    <!-- 花瓣 -->
    <path d="M 25 20 Q 23 18 25 16 Q 27 18 25 20 Z" fill="#ffb7d5" />
    <path d="M 25 20 Q 27 18 29 20 Q 27 22 25 20 Z" fill="#ffc9e0" />
    <path d="M 25 20 Q 27 22 25 24 Q 23 22 25 20 Z" fill="#ffb7d5" />
    <path d="M 25 20 Q 23 22 21 20 Q 23 18 25 20 Z" fill="#ffc9e0" />
    <circle cx="25" cy="20" r="2" fill="#ffdbeb" />
    <!-- 手绘圆圈 -->
    <path d="M 32 20 Q 32 15 28 12 Q 22 12 18 20 Q 18 28 25 28 Q 32 28 32 20 Z" 
          fill="none" stroke="#ffc9e0" stroke-width="0.8" opacity="0.3" />
  </g>

  <!-- 右侧手绘樱花 -->
  <g opacity="0.7">
    <path d="M 725 22 Q 723 20 725 18 Q 727 20 725 22 Z" fill="#ffb7d5" />
    <path d="M 725 22 Q 727 20 729 22 Q 727 24 725 22 Z" fill="#ffc9e0" />
    <path d="M 725 22 Q 727 24 725 26 Q 723 24 725 22 Z" fill="#ffb7d5" />
    <path d="M 725 22 Q 723 24 721 22 Q 723 20 725 22 Z" fill="#ffc9e0" />
    <circle cx="725" cy="22" r="2" fill="#ffdbeb" />
    <path d="M 732 22 Q 732 17 728 14 Q 722 14 718 22 Q 718 30 725 30 Q 732 30 732 22 Z" 
          fill="none" stroke="#ffc9e0" stroke-width="0.8" opacity="0.3" />
  </g>

  <!-- 小装饰元素 -->
  <circle cx="60" cy="15" r="1.5" fill="#ffb7d5" opacity="0.5" />
  <circle cx="65" cy="13" r="1" fill="#ffc9e0" opacity="0.5" />
  <circle cx="690" cy="30" r="1.5" fill="#ffb7d5" opacity="0.5" />
  <circle cx="685" cy="32" r="1" fill="#ffc9e0" opacity="0.5" />
  
  <!-- 小星星装饰 -->
  <path d="M 100 12 l 0.5 1.5 l 1.5 0.5 l -1.5 0.5 l -0.5 1.5 l -0.5 -1.5 l -1.5 -0.5 l 1.5 -0.5 z" 
        fill="#ffc9e0" opacity="0.4" />
  <path d="M 650 32 l 0.5 1.5 l 1.5 0.5 l -1.5 0.5 l -0.5 1.5 l -0.5 -1.5 l -1.5 -0.5 l 1.5 -0.5 z" 
        fill="#ffc9e0" opacity="0.4" />

  <!-- 纸胶带效果（左） -->
  <rect x="8" y="18" width="8" height="10" rx="1" fill="#ffc9e0" opacity="0.2" />
  
  <!-- 纸胶带效果（右） -->
  <rect x="734" y="18" width="8" height="10" rx="1" fill="#ffb7d5" opacity="0.2" />

  <!-- 文字 -->
  <text x="375" y="24" text-anchor="middle" dominant-baseline="central">
    <tspan class="text">✿ あなたは</tspan>
    <tspan class="count" dx="2">${escapeXml(paddedCount)}</tspan>
    <tspan class="text" dx="2">人目の訪問者です。 ✿</tspan>
  </text>

  <style>
    @import url('https://fonts.googleapis.com/css2?family=Klee+One:wght@400;600&amp;display=swap');
    
    .text {
      fill: #8b6680;
      font-family: "Klee One", "Yuji Syuku", "Hiragino Maru Gothic ProN", cursive;
      font-size: 17px;
      font-weight: 400;
      letter-spacing: 0.5px;
    }
    .count {
      fill: #d45a7a;
      font-family: "Klee One", "Yuji Syuku", "Hiragino Maru Gothic ProN", cursive;
      font-size: 21px;
      font-weight: 600;
      letter-spacing: 1.5px;
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
