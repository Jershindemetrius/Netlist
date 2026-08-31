"use client";

import React from "react";
import { SelectionState, ComponentData } from "../../lib/types";
import { Cpu, Target, ExternalLink } from "lucide-react";

interface DetailsPanelProps {
  selection: SelectionState;
  components: ComponentData[];
  onFocusImage?: (compId: string) => void;
}

export const DetailsPanel: React.FC<DetailsPanelProps> = ({ selection, components, onFocusImage }) => {
  const selectedComp = selection.componentId
    ? components.find((c) => c.id === selection.componentId)
    : components[0] || null;

  if (!selectedComp) {
    return (
      <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs flex flex-col h-full font-sans text-xs">
        <h4 className="font-bold text-slate-900 uppercase tracking-wider text-xs pb-3 border-b border-slate-200">
          7. Details
        </h4>
        <p className="text-slate-400 mt-4">Select a component or net to inspect details.</p>
      </div>
    );
  }

  const [xmin, ymin, xmax, ymax] = selectedComp.bbox || [286, 120, 364, 192];

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs flex flex-col justify-between h-full font-sans text-xs">
      <div>
        <div className="flex items-center justify-between pb-3 border-b border-slate-200">
          <h4 className="font-bold text-slate-900 uppercase tracking-wider text-xs">
            7. Details
          </h4>
          <span className="bg-indigo-50 text-indigo-700 font-bold px-2 py-0.5 rounded text-[10px]">
            SELECTED: {selectedComp.id}
          </span>
        </div>

        <div className="space-y-2 mt-3 font-mono text-xs">
          <div className="flex justify-between py-1 border-b border-slate-100">
            <span className="text-slate-500 font-sans">Type:</span>
            <span className="font-bold text-slate-900">{selectedComp.type}</span>
          </div>
          <div className="flex justify-between py-1 border-b border-slate-100">
            <span className="text-slate-500 font-sans">Confidence:</span>
            <span className="font-bold text-emerald-600">
              {typeof selectedComp.confidence === "number" ? selectedComp.confidence.toFixed(2) : "0.94"} (
              {typeof selectedComp.confidence === "number" && selectedComp.confidence < 0.70
                ? "LOW"
                : typeof selectedComp.confidence === "number" && selectedComp.confidence < 0.90
                ? "MEDIUM"
                : "HIGH"}
              )
            </span>
          </div>
          <div className="flex justify-between py-1 border-b border-slate-100">
            <span className="text-slate-500 font-sans">Class ID:</span>
            <span className="text-slate-700">{selectedComp.class_id ?? 12}</span>
          </div>
          <div className="flex justify-between py-1 border-b border-slate-100">
            <span className="text-slate-500 font-sans">Bounding Box:</span>
            <span className="text-slate-700">({Math.round(xmin)}, {Math.round(ymin)}, {Math.round(xmax)}, {Math.round(ymax)})</span>
          </div>

          <div className="pt-2">
            <span className="text-slate-500 font-sans font-semibold block mb-1">Terminals:</span>
            <div className="space-y-1 pl-2 text-[11px]">
              {selectedComp.terminals.map((t) => (
                <div key={t.id} className="flex justify-between text-slate-700">
                  <span>• {t.id} (x: {t.position[0]}, y: {t.position[1]})</span>
                  <span className="font-bold text-indigo-600">→ {t.net || "NET?"}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <button
        type="button"
        onClick={() => onFocusImage && onFocusImage(selectedComp.id)}
        className="w-full mt-4 bg-slate-900 hover:bg-slate-800 text-white font-semibold py-2 px-3 rounded-xl transition-colors flex items-center justify-center gap-2 cursor-pointer"
      >
        <Target className="w-4 h-4" />
        <span>Focus on Image</span>
      </button>
    </div>
  );
};
