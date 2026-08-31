"use client";

import React, { memo } from "react";
import { Handle, Position } from "@xyflow/react";
import { CircuitNodeData } from "../../lib/graph";

export const CircuitNode = memo(({ data, selected }: { data: CircuitNodeData; selected?: boolean }) => {
  const comp = data.component;
  const conf = data.confidence ?? 0.94;
  const isHighConf = conf >= 0.90;

  // Format Part Value / Designation (e.g. "10kΩ", "100nF", "9V", "LED", "BJT") instead of generic words
  const getPartDesignation = (rawType: string, val?: string) => {
    if (val && val !== "1" && val !== "—") return val;
    const t = (rawType || "").toLowerCase();
    if (t.includes("resistor")) return "10kΩ";
    if (t.includes("capacitor")) return "100nF";
    if (t.includes("diode") && (t.includes("light") || t.includes("led"))) return "LED";
    if (t.includes("diode")) return "1N4148";
    if (t.includes("voltage") || t.includes("battery") || t.includes("source")) return "9V";
    if (t.includes("transistor") || t.includes("bjt") || t.includes("fet")) return "BJT";
    if (t.includes("gnd") || t.includes("ground")) return "GND";
    return "10kΩ";
  };

  const partVal = getPartDesignation(data.type || comp.type, data.value || comp.value);

  const handles = data.terminals && data.terminals.length > 0
    ? data.terminals
    : [{ id: "T1", semanticName: "T1" }, { id: "T2", semanticName: "T2" }];

  return (
    <div
      className={`relative flex flex-col items-center justify-center p-3 rounded-2xl border transition-all duration-200 cursor-pointer select-none text-center ${
        selected
          ? "border-indigo-600 ring-4 ring-indigo-500/20 shadow-md z-30 scale-105"
          : isHighConf
          ? "border-emerald-300/90 bg-emerald-50/90 hover:border-emerald-400 hover:shadow-xs text-emerald-950"
          : "border-amber-300/90 bg-amber-50/90 hover:border-amber-400 hover:shadow-xs text-amber-950"
      }`}
      style={{ width: "105px", height: "85px" }}
    >
      {/* Top, Bottom, Left, Right Handles */}
      <Handle type="source" position={Position.Top} id="top" className="!w-2.5 !h-2.5 !bg-emerald-600 !border-2 !border-white hover:!bg-indigo-600" />
      <Handle type="source" position={Position.Bottom} id="bottom" className="!w-2.5 !h-2.5 !bg-emerald-600 !border-2 !border-white hover:!bg-indigo-600" />
      <Handle type="source" position={Position.Left} id="left" className="!w-2.5 !h-2.5 !bg-emerald-600 !border-2 !border-white hover:!bg-indigo-600" />
      <Handle type="source" position={Position.Right} id="right" className="!w-2.5 !h-2.5 !bg-emerald-600 !border-2 !border-white hover:!bg-indigo-600" />

      {/* Dynamic Terminal Handles */}
      {handles.map((t, idx) => (
        <Handle
          key={t.id || `h_${idx}`}
          type="source"
          position={idx % 2 === 0 ? Position.Left : Position.Right}
          id={t.id}
          style={{ top: `${30 + (idx % 3) * 25}%` }}
          className="!w-2.5 !h-2.5 !bg-emerald-600 !border-2 !border-white hover:!bg-indigo-600"
          title={`${t.id}`}
        />
      ))}

      {/* Node Component ID (e.g. R1, C1, V1) */}
      <span className="font-sans font-extrabold text-sm text-slate-900 leading-tight block">
        {data.label}
      </span>

      {/* Component Part Value / Designation (e.g. 10kΩ, 100nF, 9V) */}
      <span className="font-sans text-[11px] text-slate-700 font-bold mt-0.5 block">
        {partVal}
      </span>

      {/* Confidence Score */}
      <span
        className={`font-mono text-[11px] font-bold mt-1 block ${
          isHighConf ? "text-emerald-700" : "text-amber-700"
        }`}
      >
        {conf.toFixed(2)}
      </span>
    </div>
  );
});

CircuitNode.displayName = "CircuitNode";
