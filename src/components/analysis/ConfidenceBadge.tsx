"use client";

import React from "react";
import { AlertTriangle, CheckCircle2 } from "lucide-react";

interface ConfidenceBadgeProps {
  confidence: number;
  showIcon?: boolean;
  size?: "sm" | "md";
}

export const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({
  confidence,
  showIcon = true,
  size = "md",
}) => {
  const numericConf = typeof confidence === "number" && !isNaN(confidence) ? confidence : 0.94;
  const percent = Math.round(numericConf * 100);
  const isHigh = numericConf >= 0.85;
  const isMedium = numericConf >= 0.70 && numericConf < 0.85;
  const isLow = numericConf < 0.70;

  let colorClasses = "bg-neutral-100 text-neutral-900 border-neutral-300";
  if (isHigh) {
    colorClasses = "bg-emerald-50 text-emerald-800 border-emerald-300";
  } else if (isMedium) {
    colorClasses = "bg-amber-50 text-amber-900 border-amber-300";
  } else if (isLow) {
    colorClasses = "bg-red-50 text-red-800 border-red-300 animate-pulse";
  }

  const textSize = size === "sm" ? "text-xs px-2 py-0.5" : "text-xs px-2.5 py-1";

  return (
    <span
      className={`inline-flex items-center gap-1 font-mono font-semibold rounded-md border ${textSize} ${colorClasses}`}
    >
      {showIcon && (
        isLow ? (
          <AlertTriangle className="w-3 h-3 text-red-600" />
        ) : (
          <CheckCircle2 className="w-3 h-3 text-emerald-600" />
        )
      )}
      <span>{percent}%</span>
      {isLow && <span className="font-sans font-semibold tracking-wide ml-0.5">Uncertain</span>}
    </span>
  );
};
