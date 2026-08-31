"use client";

import React from "react";
import { Zap, ArrowRight } from "lucide-react";

export const SimplificationPanel: React.FC = () => {
  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs flex flex-col h-full font-sans text-xs">
      <div className="flex items-center justify-between pb-3 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <div className="p-1 rounded bg-amber-50 text-amber-600">
            <Zap className="w-4 h-4" />
          </div>
          <h4 className="font-bold text-slate-900 uppercase tracking-wider text-xs">
            6. Simplification (Beta)
          </h4>
        </div>
        <span className="text-[10px] text-slate-400">Detected Simplifications (2)</span>
      </div>

      <div className="space-y-4 mt-3 flex-1 overflow-y-auto">
        {/* Series Resistors */}
        <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
          <div className="flex items-center justify-between font-bold text-slate-800">
            <span>Series Resistors</span>
            <span className="font-mono text-indigo-600">R1 + R2</span>
          </div>
          <div className="flex items-center justify-center gap-3 bg-white p-2.5 rounded-lg border border-slate-200">
            <span className="font-mono text-slate-700">R1 — MMMM — R2</span>
            <ArrowRight className="w-4 h-4 text-slate-400" />
            <span className="font-mono font-bold text-indigo-700">Req = R1 + R2</span>
          </div>
        </div>

        {/* Parallel Resistors */}
        <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
          <div className="flex items-center justify-between font-bold text-slate-800">
            <span>Parallel Resistors</span>
            <span className="font-mono text-indigo-600">R3 || R4</span>
          </div>
          <div className="flex items-center justify-center gap-3 bg-white p-2.5 rounded-lg border border-slate-200">
            <span className="font-mono text-slate-700">R3 || R4</span>
            <ArrowRight className="w-4 h-4 text-slate-400" />
            <span className="font-mono font-bold text-indigo-700">Req = (R3·R4)/(R3+R4)</span>
          </div>
        </div>
      </div>
      <p className="text-[10px] text-slate-400 mt-2">Note: Simplification supports resistors and capacitors only.</p>
    </div>
  );
};
