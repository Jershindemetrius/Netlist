"use client";

import React, { memo } from "react";
import { Handle, Position } from "@xyflow/react";
import { NetNodeData } from "../../lib/graph";
import { Network, Zap } from "lucide-react";

export const CircuitNetNode = memo(({ data, selected }: { data: NetNodeData; selected?: boolean }) => {
  const isGnd = data.netId === "0" || data.netId.toUpperCase().includes("GND");

  return (
    <div
      className={`relative px-3 py-1.5 rounded-full border-2 shadow-sm font-mono text-xs font-bold transition-all duration-150 flex items-center gap-1.5 ${
        selected
          ? "border-black bg-black text-white ring-4 ring-black/20 z-30"
          : isGnd
          ? "border-emerald-600 bg-emerald-50 text-emerald-900"
          : "border-black bg-white text-black hover:bg-neutral-100"
      }`}
    >
      <Handle type="target" position={Position.Top} className="!w-2 !h-2 !bg-black" />
      <Network className="w-3.5 h-3.5" />
      <span>{data.netId}</span>
      <Handle type="source" position={Position.Bottom} className="!w-2 !h-2 !bg-black" />
    </div>
  );
});

CircuitNetNode.displayName = "CircuitNetNode";
