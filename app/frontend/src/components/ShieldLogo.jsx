import React from react;

export function ShieldLogo({ className = \"\" }) {
  return (
    <svg viewBox=\"0 0 64 64\" className={className} xmlns=\"http://www.w3.org/2000/svg\">
      <defs>
        <linearGradient id=\"shieldGold\" x1=\"0\" x2=\"1\" y1=\"0\" y2=\"1\">
          <stop offset=\"0%\" stopColor=\"#e3cb96\" />
          <stop offset=\"50%\" stopColor=\"#c8a96e\" />
          <stop offset=\"100%\" stopColor=\"#8f7442\" />
        </linearGradient>
        <radialGradient id=\"eyeBlue\" cx=\"50%\" cy=\"50%\" r=\"50%\">
          <stop offset=\"0%\" stopColor=\"#e3f6ff\" />
          <stop offset=\"50%\" stopColor=\"#4fc3f7\" />
          <stop offset=\"100%\" stopColor=\"#0a5a7f\" />
        </radialGradient>
      </defs>
      <path
        d=\"M32 4 L58 12 L58 30 C58 46 47 56 32 60 C17 56 6 46 6 30 L6 12 Z\"
        fill=\"url(#shieldGold)\"
        stroke=\"#0a0a0f\"
        strokeWidth=\"1.5\"
      />
      <path
        d=\"M32 9 L52 15.5 L52 30 C52 42 43 50.5 32 54 C21 50.5 12 42 12 30 L12 15.5 Z\"
        fill=\"#0a0a0f\"
      />
      {/* Eye */}
      <path
        d=\"M14 32 C20 22 26 19 32 19 C38 19 44 22 50 32 C44 42 38 45 32 45 C26 45 20 42 14 32 Z\"
        fill=\"#05050a\"
        stroke=\"#c8a96e\"
        strokeWidth=\"1.1\"
      />
      <circle cx=\"32\" cy=\"32\" r=\"7\" fill=\"url(#eyeBlue)\" />
      <circle cx=\"32\" cy=\"32\" r=\"3\" fill=\"#05050a\" />
      <circle cx=\"30\" cy=\"30\" r=\"1.1\" fill=\"#eaffff\" />
      {/* Scan lines across eye */}
      <line x1=\"14\" y1=\"28\" x2=\"50\" y2=\"28\" stroke=\"rgba(79,195,247,0.25)\" strokeWidth=\"0.4\" />
      <line x1=\"14\" y1=\"36\" x2=\"50\" y2=\"36\" stroke=\"rgba(79,195,247,0.25)\" strokeWidth=\"0.4\" />
      {/* Crosshair ticks */}
      <line x1=\"32\" y1=\"17\" x2=\"32\" y2=\"21\" stroke=\"#c8a96e\" strokeWidth=\"0.9\" />
      <line x1=\"32\" y1=\"43\" x2=\"32\" y2=\"47\" stroke=\"#c8a96e\" strokeWidth=\"0.9\" />
    </svg>
  );
}
