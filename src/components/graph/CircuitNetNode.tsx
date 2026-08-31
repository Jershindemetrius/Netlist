"use client";

import React, { memo } from "react";
import { Handle, Position } from "@xyflow/react";
import { NetNodeData } from "../../lib/graph";

export const CircuitNetNode = memo(({ data, selected }: { data: NetNodeData; selected?: boolean }) => {
  const isGnd = data.netId === "0" || data.netId.toUpperCase().includes("GND");
  const displayLabel = isGnd && !data.netId.includes("GND") ? "NET4 (GND)" : data.netId;

  return (
    <div className="relative flex flex-col items-center justify-center select-none">
      <div
        className={`relative inline-flex items-center justify-center px-3.5 py-1.5 rounded-full border text-xs font-bold transition-all duration-200 cursor-pointer shadow-xs ${
          selected
            ? "border-indigo-600 bg-indigo-600 text-white ring-4 ring-indigo-500/20 shadow-md scale-105 z-30"
            : "border-indigo-200 bg-indigo-50/90 hover:bg-indigo-100/90 text-indigo-900"
        }`}
      >
        <Handle type="target" position={Position.Top} className="!w-2 !h-2 !bg-indigo-600 !border !border-white" />
        <Handle type="source" position={Position.Bottom} className="!w-2 !h-2 !bg-indigo-600 !border !border-white" />
        <Handle type="target" position={Position.Left} className="!w-2 !h-2 !bg-indigo-600 !border !border-white" />
        <Handle type="source" position={Position.Right} className="!w-2 !h-2 !bg-indigo-600 !border !border-white" />

        <span>{displayLabel}</span>
      </div>

      {/* Electrical Ground Symbol (3 decreasing horizontal lines) */}
      {isGnd && (
        <div className="flex flex-col items-center mt-1 space-y-0.5">
          <div className="w-0.5 h-2 bg-slate-700" />
          <div className="w-5 h-0.5 bg-slate-700" />
          <div className="w-3 h-0.5 bg-slate-700" />
          <div className="w-1.5 h-0.5 bg-slate-700" />
        </div>
      )}
    </div>
  );
});

CircuitNetNode.displayName = "CircuitNetNode";
