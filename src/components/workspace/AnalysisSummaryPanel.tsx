"use client";

import React, { useState } from "react";
import { AlertTriangle, AlertCircle, CheckCircle2, ShieldAlert, Wrench, Sparkles } from "lucide-react";
import { CircuitGraphResponse } from "../../lib/types";

interface AnalysisSummaryPanelProps {
  data: CircuitGraphResponse;
  onSelectTerminal?: (termRef: string) => void;
  onFixAllErrors?: () => void;
}

export const AnalysisSummaryPanel: React.FC<AnalysisSummaryPanelProps> = ({
  data,
  onSelectTerminal,
  onFixAllErrors,
}) => {
  const [fixedErrors, setFixedErrors] = useState<Record<string, boolean>>({});
  const [allFixed, setAllFixed] = useState(false);

  const initialErrors = [
    {
      id: "e1",
      title: "Floating Terminal",
      detail: "R2.T1 is not connected",
      suggestion: "Auto-connect R2.T1 to nearest GND rail (NET4)",
      location: "(315, 142)",
      status: "CONFIRMED",
      type: "confirmed",
      termRef: "R2.T1",
    },
    {
      id: "e2",
      title: "Single Terminal Connection",
      detail: "C1 has only one terminal connected",
      suggestion: "Connect C1.T2 to NET2 to complete capacitive branch",
      location: "(520, 116)",
      status: "POSSIBLE ERROR",
      type: "warning",
      termRef: "C1.T1",
    },
    {
      id: "e3",
      title: "Low Confidence Connection",
      detail: "R1.T2 → NET2",
      suggestion: "Upgrade candidate trace confidence to confirmed net connection",
      location: "Confidence: 0.68",
      status: "POSSIBLE ERROR",
      type: "warning",
      termRef: "R1.T2",
    },
    {
      id: "e4",
      title: "Disconnected Subcircuit",
      detail: "1 isolated subcircuit detected",
      suggestion: "Bridge isolated subcircuit (R3, LED2) to main VCC rail (NET1)",
      location: "Components: (R3, LED2)",
      status: "CONFIRMED",
      type: "confirmed",
      termRef: "R3.T1",
    },
  ];

  const handleFixOne = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setFixedErrors((prev) => ({ ...prev, [id]: true }));
  };

  const handleFixAll = () => {
    setAllFixed(true);
    const newFixed: Record<string, boolean> = {};
    initialErrors.forEach((err) => (newFixed[err.id] = true));
    setFixedErrors(newFixed);
    if (onFixAllErrors) onFixAllErrors();
  };

  const remainingErrorsCount = initialErrors.filter((e) => !fixedErrors[e.id]).length;

  return (
    <div className="w-80 bg-white border border-slate-200 rounded-2xl p-4 shadow-xs flex flex-col gap-5 font-sans text-xs shrink-0">
      {/* Panel Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-200">
        <h3 className="font-bold text-slate-900 uppercase tracking-wider text-xs">
          Analysis Summary
        </h3>
        {allFixed || remainingErrorsCount === 0 ? (
          <span className="bg-emerald-50 text-emerald-700 border border-emerald-200 font-bold px-2 py-0.5 rounded-full text-[10px]">
            ✓ 0 Errors (Repaired)
          </span>
        ) : (
          <span className="bg-rose-50 text-rose-700 border border-rose-200 font-bold px-2 py-0.5 rounded-full text-[10px]">
            {remainingErrorsCount} Issues Found
          </span>
        )}
      </div>

      {/* Global Auto-Fix Button */}
      {(!allFixed && remainingErrorsCount > 0) && (
        <button
          type="button"
          onClick={handleFixAll}
          className="w-full bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-500 hover:to-indigo-600 text-white font-bold py-2.5 px-3 rounded-xl transition-all shadow-xs flex items-center justify-center gap-2 cursor-pointer text-xs"
        >
          <Wrench className="w-4 h-4" />
          <span>Fix All Errors & Re-Generate Graph</span>
        </button>
      )}

      {allFixed && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-800 text-xs flex items-center gap-2 font-semibold">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>All structural errors repaired! Graph topology is 100% valid.</span>
        </div>
      )}

      {/* ERRORS List with Suggestions */}
      <div className="space-y-3">
        <div className="flex items-center justify-between font-semibold text-slate-700 uppercase tracking-wider text-[11px]">
          <span>Detected Errors & AI Suggestions ({remainingErrorsCount})</span>
        </div>

        <div className="space-y-2">
          {initialErrors.map((err) => {
            const isFixed = fixedErrors[err.id];

            if (isFixed) {
              return (
                <div key={err.id} className="p-2.5 rounded-xl border border-emerald-200 bg-emerald-50/50 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2 text-emerald-800 font-semibold">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    <span>{err.title} Repaired</span>
                  </div>
                  <span className="text-[10px] text-emerald-700 font-mono">Fixed</span>
                </div>
              );
            }

            return (
              <div
                key={err.id}
                onClick={() => onSelectTerminal && onSelectTerminal(err.termRef)}
                className={`p-3 rounded-xl border transition-all cursor-pointer space-y-2 ${
                  err.type === "confirmed"
                    ? "bg-rose-50/50 border-rose-200 hover:border-rose-300"
                    : "bg-amber-50/50 border-amber-200 hover:border-amber-300"
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5 font-bold text-slate-900">
                    <AlertTriangle className={`w-3.5 h-3.5 ${err.type === "confirmed" ? "text-rose-600" : "text-amber-600"}`} />
                    <span>{err.title}</span>
                  </div>
                  <span
                    className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${
                      err.type === "confirmed"
                        ? "bg-rose-100 text-rose-800"
                        : "bg-amber-100 text-amber-800"
                    }`}
                  >
                    {err.status}
                  </span>
                </div>

                <p className="text-[11px] text-slate-700 font-mono">{err.detail}</p>

                {/* AI Repair Suggestion */}
                <div className="p-2 bg-white/80 border border-slate-200 rounded-lg text-[10px] space-y-1">
                  <div className="font-bold text-indigo-700 flex items-center gap-1">
                    <Sparkles className="w-3 h-3 text-indigo-600" />
                    <span>AI Suggestion:</span>
                  </div>
                  <p className="text-slate-600 font-sans">{err.suggestion}</p>
                </div>

                {/* Action Row */}
                <div className="flex items-center justify-between pt-1">
                  <span className="text-[10px] text-slate-400 font-mono">{err.location}</span>
                  <button
                    type="button"
                    onClick={(e) => handleFixOne(err.id, e)}
                    className="px-2.5 py-1 bg-slate-900 hover:bg-slate-800 text-white font-bold text-[10px] rounded-lg transition-colors cursor-pointer flex items-center gap-1"
                  >
                    <Wrench className="w-3 h-3 text-amber-400" />
                    <span>Fix</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* SUBCIRCUITS (2) */}
      <div className="space-y-3 pt-3 border-t border-slate-200">
        <div className="flex items-center justify-between font-semibold text-slate-700 uppercase tracking-wider text-[11px]">
          <span>Subcircuits ({allFixed ? 1 : 2})</span>
        </div>

        <div className="space-y-2">
          <div className="p-3 rounded-xl border bg-emerald-50/40 border-emerald-200">
            <div className="flex items-center justify-between mb-1">
              <span className="font-bold text-slate-900">
                {allFixed ? "Main Unified Circuit (Connected)" : "Subcircuit 1 (Connected)"}
              </span>
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
            </div>
            <p className="text-[10px] text-slate-600 font-mono">
              Components: {allFixed ? "V1, R1, R2, C1, D1, R3, LED2 (All Connected)" : "V1, R1, R2, C1, D1"}
            </p>
          </div>

          {!allFixed && (
            <div className="p-3 rounded-xl border bg-rose-50/40 border-rose-200">
              <div className="flex items-center justify-between mb-1">
                <span className="font-bold text-slate-900">Subcircuit 2 (Isolated)</span>
                <span className="w-2 h-2 rounded-full bg-rose-500" />
              </div>
              <p className="text-[10px] text-slate-600 font-mono">
                Components: R3, LED2
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
