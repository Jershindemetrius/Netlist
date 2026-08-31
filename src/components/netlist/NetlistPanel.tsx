"use client";

import React, { useState } from "react";
import { CircuitGraphResponse, SelectionState } from "../../lib/types";
import { NetlistRow } from "./NetlistRow";
import { exportCircuitJson, exportSpiceNetlist } from "../../lib/export";
import { FileCode, Download, Cpu, AlertTriangle } from "lucide-react";

interface NetlistPanelProps {
  data: CircuitGraphResponse;
  selection: SelectionState;
  onSelectNet: (netId: string | null) => void;
  onSelectTerminal: (termRef: string | null) => void;
  onSelectComponent: (id: string | null) => void;
}

export const NetlistPanel: React.FC<NetlistPanelProps> = ({
  data,
  selection,
  onSelectNet,
  onSelectTerminal,
  onSelectComponent,
}) => {
  const [viewMode, setViewMode] = useState<"net" | "component" | "spice">("net");

  // Collect low confidence terminals map
  const lowConfTerms: Record<string, number> = {};
  data.components.forEach((comp) => {
    comp.terminals.forEach((term) => {
      const conf = term.confidence ?? comp.confidence;
      if (conf < 0.70) {
        lowConfTerms[`${comp.id}.${term.id}`] = conf;
      }
    });
  });

  const spiceText = data.components.length > 0
    ? generateSpiceText(data)
    : "* Empty Netlist";

  return (
    <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-xs flex flex-col h-full">
      {/* Header & Controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 px-6 py-4 border-b border-slate-200 bg-slate-50/50">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-indigo-50 text-indigo-600">
            <FileCode className="w-4 h-4" />
          </div>
          <h3 className="text-sm font-bold text-slate-900">
            Reconstructed Netlist & Electrical Topology
          </h3>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* View Mode Toggle */}
          <div className="inline-flex rounded-xl border border-slate-200 p-0.5 bg-slate-100 text-xs font-semibold">
            <button
              type="button"
              onClick={() => setViewMode("net")}
              className={`px-3 py-1 rounded-lg transition-colors cursor-pointer ${
                viewMode === "net"
                  ? "bg-white text-slate-900 shadow-2xs font-bold"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              Nets View
            </button>
            <button
              type="button"
              onClick={() => setViewMode("component")}
              className={`px-3 py-1 rounded-lg transition-colors cursor-pointer ${
                viewMode === "component"
                  ? "bg-white text-slate-900 shadow-2xs font-bold"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              Components View
            </button>
            <button
              type="button"
              onClick={() => setViewMode("spice")}
              className={`px-3 py-1 rounded-lg transition-colors cursor-pointer ${
                viewMode === "spice"
                  ? "bg-white text-slate-900 shadow-2xs font-bold"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              SPICE Code (.cir)
            </button>
          </div>

          {/* Export Actions */}
          <button
            type="button"
            onClick={() => exportCircuitJson(data)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 rounded-xl shadow-2xs cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" />
            <span>JSON</span>
          </button>
          <button
            type="button"
            onClick={() => exportSpiceNetlist(data)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl shadow-2xs cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" />
            <span>SPICE</span>
          </button>
        </div>
      </div>

      {/* Content View Area */}
      <div className="p-6 overflow-y-auto max-h-[500px]">
        {/* Net View */}
        {viewMode === "net" && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(data.nets || {}).map(([netId, termList]) => (
              <NetlistRow
                key={netId}
                netId={netId}
                terminals={termList}
                selection={selection}
                onSelectNet={onSelectNet}
                onSelectTerminal={onSelectTerminal}
                lowConfTerms={lowConfTerms}
              />
            ))}
          </div>
        )}

        {/* Component View */}
        {viewMode === "component" && (
          <div className="space-y-3 text-xs">
            {data.components.map((comp) => {
              const isSelected =
                selection.type === "component" && selection.componentId === comp.id;

              return (
                <div
                  key={comp.id}
                  onClick={() => onSelectComponent(isSelected ? null : comp.id)}
                  className={`p-4 border rounded-xl cursor-pointer transition-all ${
                    isSelected
                      ? "border-indigo-600 bg-indigo-50/50 ring-2 ring-indigo-500/20"
                      : "border-slate-200 bg-white hover:border-slate-300"
                  }`}
                >
                  <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-100">
                    <div className="flex items-center gap-2">
                      <Cpu className="w-4 h-4 text-indigo-600" />
                      <span className="font-bold text-slate-900">{comp.id}</span>
                      <span className="text-slate-500">({comp.type})</span>
                    </div>
                    {comp.value && (
                      <span className="bg-slate-100 text-slate-900 font-bold px-2 py-0.5 rounded border border-slate-200">
                        {comp.value}
                      </span>
                    )}
                  </div>

                  <div className="space-y-1 pl-4">
                    {comp.terminals.map((t) => {
                      const termRef = `${comp.id}.${t.id}`;
                      const isLowConf = (t.confidence ?? comp.confidence) < 0.70;

                      return (
                        <div key={t.id} className="flex items-center justify-between text-slate-700">
                          <span>
                            {t.id} <span className="text-slate-400">→</span>{" "}
                            <span className="font-bold text-slate-900">{t.net || "NC"}</span>
                          </span>
                          {isLowConf && (
                            <span className="inline-flex items-center gap-1 text-[10px] text-amber-700 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200 font-semibold">
                              <AlertTriangle className="w-3 h-3 text-amber-600" />
                              Uncertain ({Math.round((t.confidence ?? comp.confidence) * 100)}%)
                            </span>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* SPICE Code View */}
        {viewMode === "spice" && (
          <div className="bg-slate-900 text-slate-100 rounded-xl p-5 font-mono text-xs overflow-x-auto shadow-inner">
            <pre className="whitespace-pre-wrap leading-relaxed">{spiceText}</pre>
          </div>
        )}
      </div>
    </div>
  );
};

function generateSpiceText(data: CircuitGraphResponse): string {
  const lines: string[] = [
    `* NETLIST Reconstructed Circuit Netlist`,
    `* Image ID: ${data.image_id}`,
    `* Confidence: ${Math.round(data.confidence * 100)}%`,
    ``
  ];

  const termToNet: Record<string, string> = {};
  Object.entries(data.nets || {}).forEach(([netId, termList]) => {
    termList.forEach((ref) => {
      termToNet[ref] = netId;
    });
  });

  data.components.forEach((comp) => {
    const pins = comp.terminals.map((t) => termToNet[`${comp.id}.${t.id}`] || "0");
    lines.push(`${comp.id} ${pins.join(" ")} ${comp.value || "1"}`);
  });

  lines.push(``, `.end`);
  return lines.join("\n");
}
