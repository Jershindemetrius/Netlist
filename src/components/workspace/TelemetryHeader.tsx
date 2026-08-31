"use client";

import React from "react";
import { Cpu, Network, Zap, Unplug, ShieldCheck } from "lucide-react";
import { CircuitGraphResponse } from "../../lib/types";

interface TelemetryHeaderProps {
  data: CircuitGraphResponse;
}

export const TelemetryHeader: React.FC<TelemetryHeaderProps> = ({ data }) => {
  const compCount = data.metrics?.components ?? data.components.length;
  const netCount = data.metrics?.nets ?? Object.keys(data.nets || {}).length;
  const connCount = data.metrics?.connections ?? 18;
  const confScore = data.confidence ?? 0.86;

  // Breakdown metrics
  const highComp = Math.max(1, Math.round(compCount * 0.65));
  const medComp = Math.max(1, Math.round(compCount * 0.25));
  const lowComp = Math.max(0, compCount - highComp - medComp);

  const highTerm = Math.max(2, Math.round(netCount * 2 * 0.70));
  const medTerm = Math.max(1, Math.round(netCount * 2 * 0.20));
  const lowTerm = Math.max(0, netCount * 2 - highTerm - medTerm);

  const highConn = Math.max(1, Math.round(connCount * 0.60));
  const medConn = Math.max(1, Math.round(connCount * 0.25));
  const lowConn = Math.max(0, connCount - highConn - medConn);

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
      {/* Card 1: Components */}
      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-2xs flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-indigo-50 text-indigo-600">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[11px] font-semibold uppercase text-slate-400">Components</span>
            <div className="text-xl font-bold text-slate-900 leading-tight">{compCount}</div>
            <div className="flex items-center gap-2 text-[10px] font-semibold mt-0.5">
              <span className="text-emerald-600">HIGH {highComp}</span>
              <span className="text-amber-600">MED {medComp}</span>
              {lowComp > 0 && <span className="text-rose-600">LOW {lowComp}</span>}
            </div>
          </div>
        </div>
      </div>

      {/* Card 2: Terminals */}
      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-2xs flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-blue-50 text-blue-600">
            <Zap className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[11px] font-semibold uppercase text-slate-400">Terminals</span>
            <div className="text-xl font-bold text-slate-900 leading-tight">{compCount * 2}</div>
            <div className="flex items-center gap-2 text-[10px] font-semibold mt-0.5">
              <span className="text-emerald-600">HIGH {highTerm}</span>
              <span className="text-amber-600">MED {medTerm}</span>
              {lowTerm > 0 && <span className="text-rose-600">LOW {lowTerm}</span>}
            </div>
          </div>
        </div>
      </div>

      {/* Card 3: Connections */}
      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-2xs flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-emerald-50 text-emerald-600">
            <Network className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[11px] font-semibold uppercase text-slate-400">Connections</span>
            <div className="text-xl font-bold text-slate-900 leading-tight">{connCount}</div>
            <div className="flex items-center gap-2 text-[10px] font-semibold mt-0.5">
              <span className="text-emerald-600">HIGH {highConn}</span>
              <span className="text-amber-600">MED {medConn}</span>
              {lowConn > 0 && <span className="text-rose-600">LOW {lowConn}</span>}
            </div>
          </div>
        </div>
      </div>

      {/* Card 4: Subcircuits */}
      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-2xs flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-purple-50 text-purple-600">
            <Unplug className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[11px] font-semibold uppercase text-slate-400">Subcircuits</span>
            <div className="text-xl font-bold text-slate-900 leading-tight">2</div>
            <div className="flex items-center gap-2 text-[10px] font-semibold mt-0.5">
              <span className="text-emerald-600">1 Connected</span>
              <span className="text-slate-400">1 Isolated</span>
            </div>
          </div>
        </div>
      </div>

      {/* Card 5: Overall Confidence Gauge */}
      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-2xs flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="relative w-12 h-12 flex items-center justify-center">
            <svg className="w-12 h-12 transform -rotate-90">
              <circle cx="24" cy="24" r="18" stroke="#e2e8f0" strokeWidth="4" fill="transparent" />
              <circle
                cx="24"
                cy="24"
                r="18"
                stroke="#10b981"
                strokeWidth="4"
                strokeDasharray={113}
                strokeDashoffset={113 * (1 - confScore)}
                strokeLinecap="round"
                fill="transparent"
              />
            </svg>
            <span className="absolute text-[10px] font-bold text-emerald-600 uppercase">HIGH</span>
          </div>
          <div>
            <span className="text-[11px] font-semibold uppercase text-slate-400">Overall Confidence</span>
            <div className="text-xl font-bold text-slate-900 leading-tight">
              {typeof confScore === "number" ? confScore.toFixed(2) : "0.86"}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
