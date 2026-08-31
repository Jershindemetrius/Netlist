"use client";

import React, { memo } from "react";
import { Handle, Position } from "@xyflow/react";
import { CircuitNodeData } from "../../lib/graph";
import { ConfidenceBadge } from "../analysis/ConfidenceBadge";
import { Cpu, AlertTriangle } from "lucide-react";

export const CircuitNode = memo(({ data, selected }: { data: CircuitNodeData; selected?: boolean }) => {
  const comp = data.component;
  const isLowConf = data.confidence < 0.70;

  return (
    <div
      className={`relative min-w-[160px] bg-white border-2 rounded-lg shadow-sm transition-all duration-150 p-3 ${
        selected
          ? "border-black ring-4 ring-black/10 scale-105 z-30"
          : isLowConf
          ? "border-amber-500 bg-amber-50/20"
          : "border-neutral-800 hover:border-black"
      }`}
    >
      <div className="flex items-center justify-between gap-2 pb-2 mb-2 border-b border-neutral-200">
        <div className="flex items-center gap-1.5">
          <Cpu className="w-4 h-4 text-black" />
          <span className="font-mono text-sm font-bold text-neutral-900">{data.label}</span>
        </div>
        <ConfidenceBadge confidence={data.confidence} size="sm" showIcon={false} />
      </div>

      <div className="space-y-1 text-xs font-mono">
        <div className="flex items-center justify-between text-neutral-600">
          <span className="text-[10px] uppercase tracking-wider text-neutral-400">Type</span>
          <span className="font-semibold text-neutral-900">{data.type}</span>
        </div>
        {data.value && (
          <div className="flex items-center justify-between text-neutral-600">
            <span className="text-[10px] uppercase tracking-wider text-neutral-400">Value</span>
            <span className="font-semibold text-black bg-neutral-100 px-1.5 py-0.5 rounded">
              {data.value}
            </span>
          </div>
        )}
      </div>

      {/* Terminal Handles */}
      <div className="mt-3 pt-2 border-t border-neutral-100 space-y-1.5">
        {data.terminals.map((t, idx) => {
          const isLeft = idx % 2 === 0;
          return (
            <div key={t.id} className="relative flex items-center justify-between text-[11px] font-mono">
              <Handle
                type="source"
                position={isLeft ? Position.Left : Position.Right}
                id={t.id}
                className="!w-2.5 !h-2.5 !bg-black !border-2 !border-white"
              />
              <span className="text-neutral-500">{t.semanticName || t.id}</span>
              <span className="font-bold text-neutral-900 bg-neutral-100 px-1 rounded">{t.net || "NC"}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
});

CircuitNode.displayName = "CircuitNode";
