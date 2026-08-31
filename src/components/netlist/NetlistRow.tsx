"use client";

import React from "react";
import { AlertTriangle, Check, Zap } from "lucide-react";
import { SelectionState } from "../../lib/types";

interface NetlistRowProps {
  netId: string;
  terminals: string[];
  selection: SelectionState;
  onSelectNet: (netId: string | null) => void;
  onSelectTerminal: (termRef: string | null) => void;
  lowConfTerms?: Record<string, number>;
}

export const NetlistRow: React.FC<NetlistRowProps> = ({
  netId,
  terminals,
  selection,
  onSelectNet,
  onSelectTerminal,
  lowConfTerms = {},
}) => {
  const isSelectedNet = selection.type === "net" && selection.netId === netId;
  const isGnd = netId === "0" || netId.toUpperCase().includes("GND");

  return (
    <div
      className={`border rounded-lg p-3 transition-all duration-150 ${
        isSelectedNet
          ? "border-black bg-neutral-100 ring-2 ring-black/10 shadow-sm"
          : isGnd
          ? "border-emerald-300 bg-emerald-50/40 hover:border-emerald-500"
          : "border-neutral-200 bg-white hover:border-neutral-400"
      }`}
    >
      <div
        onClick={() => onSelectNet(isSelectedNet ? null : netId)}
        className="flex items-center justify-between cursor-pointer pb-2 mb-2 border-b border-neutral-100"
      >
        <div className="flex items-center gap-2 font-mono text-xs font-bold text-neutral-900">
          <Zap className={`w-3.5 h-3.5 ${isGnd ? "text-emerald-600" : "text-black"}`} />
          <span>{netId}</span>
          {isGnd && (
            <span className="text-[10px] bg-emerald-100 text-emerald-800 px-1.5 py-0.2 rounded">
              GND
            </span>
          )}
        </div>
        <span className="font-mono text-[11px] text-neutral-500">
          {terminals.length} {terminals.length === 1 ? "node" : "nodes"}
        </span>
      </div>

      <div className="pl-4 space-y-1.5 font-mono text-xs">
        {terminals.map((termRef) => {
          const isSelectedTerm =
            selection.type === "terminal" && selection.terminalId === termRef;
          const conf = lowConfTerms[termRef];
          const isLowConf = conf !== undefined && conf < 0.70;

          return (
            <div
              key={termRef}
              onClick={(e) => {
                e.stopPropagation();
                onSelectTerminal(isSelectedTerm ? null : termRef);
              }}
              className={`flex items-center justify-between p-1.5 rounded cursor-pointer transition-colors ${
                isSelectedTerm
                  ? "bg-black text-white font-bold"
                  : isLowConf
                  ? "bg-amber-50 text-amber-900 border border-amber-300 hover:bg-amber-100"
                  : "hover:bg-neutral-100 text-neutral-800"
              }`}
            >
              <span className="flex items-center gap-1.5">
                <span className="text-neutral-400">•</span>
                <span>{termRef}</span>
              </span>

              {isLowConf && (
                <div className="flex items-center gap-1 text-[10px] font-bold text-amber-800 bg-amber-100 border border-amber-300 px-1.5 py-0.5 rounded">
                  <AlertTriangle className="w-3 h-3 text-amber-600" />
                  <span>Uncertain ({Math.round(conf * 100)}%)</span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
