"use client";

import React, { useState } from "react";
import {
  CircuitGraphResponse,
  SelectionState,
  ActiveTab,
} from "../../lib/types";
import { ConfidenceBadge } from "../analysis/ConfidenceBadge";
import { DetectionOverlay } from "../analysis/DetectionOverlay";
import { ComponentList } from "../analysis/ComponentList";
import { CircuitGraphView } from "../graph/CircuitGraph";
import { NetlistPanel } from "../netlist/NetlistPanel";
import { ViewModeToggle } from "./ViewModeToggle";
import {
  RotateCcw,
  Cpu,
  Zap,
  Network,
  CheckCircle2,
  AlertTriangle,
  Download,
} from "lucide-react";
import { exportCircuitJson, exportSpiceNetlist } from "../../lib/export";

interface CircuitWorkspaceProps {
  data: CircuitGraphResponse;
  imageUrl: string;
  selection: SelectionState;
  uncertainConnections: { compId: string; termId: string; netId: string; confidence: number }[];
  onSelectComponent: (id: string | null) => void;
  onSelectTerminal: (termRef: string | null) => void;
  onSelectNet: (netId: string | null) => void;
  onReset: () => void;
}

export const CircuitWorkspace: React.FC<CircuitWorkspaceProps> = ({
  data,
  imageUrl,
  selection,
  uncertainConnections,
  onSelectComponent,
  onSelectTerminal,
  onSelectNet,
  onReset,
}) => {
  const [activeTab, setActiveTab] = useState<ActiveTab>("split");

  return (
    <div className="w-full space-y-6">
      {/* Top Header & Statistics Cards */}
      <div className="bg-white border border-neutral-300 p-6 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-4 pb-6 border-b border-neutral-200">
          <div>
            <div className="flex items-center gap-3">
              <h2 className="text-2xl font-mono font-bold text-neutral-950 uppercase">
                Circuit Analysis Results
              </h2>
              <span className="font-mono text-xs bg-neutral-100 border border-neutral-300 text-neutral-800 px-2.5 py-1 font-bold">
                JOB_ID: {data.image_id}
              </span>
            </div>
            <p className="font-mono text-xs text-neutral-500 mt-1">
              Hand-drawn diagram converted to canonical CircuitGraph and SPICE netlist.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3 font-mono text-xs">
            <button
              type="button"
              onClick={() => exportCircuitJson(data)}
              className="inline-flex items-center gap-1.5 px-4 py-2 border border-neutral-400 bg-white hover:bg-neutral-100 text-neutral-900 font-bold shadow-sm"
            >
              <Download className="w-4 h-4" />
              <span>Export JSON</span>
            </button>

            <button
              type="button"
              onClick={() => exportSpiceNetlist(data)}
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-black hover:bg-neutral-800 text-white font-bold shadow-sm"
            >
              <Download className="w-4 h-4" />
              <span>Export Netlist</span>
            </button>

            <button
              type="button"
              onClick={onReset}
              className="inline-flex items-center gap-1.5 px-4 py-2 border border-neutral-300 bg-neutral-100 hover:bg-neutral-200 text-neutral-800 font-semibold"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Reset & New Scan</span>
            </button>
          </div>
        </div>

        {/* Metric Cards Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6 font-mono">
          <div className="p-4 bg-neutral-50 border border-neutral-300 flex items-center gap-3">
            <div className="p-2.5 bg-black text-white rounded-none">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[10px] uppercase font-bold text-neutral-400 tracking-wider">
                COMPONENTS
              </span>
              <p className="text-xl font-bold text-neutral-900">
                {data.metrics?.components ?? data.components.length}
              </p>
            </div>
          </div>

          <div className="p-4 bg-neutral-50 border border-neutral-300 flex items-center gap-3">
            <div className="p-2.5 bg-black text-lime-400 rounded-none">
              <Zap className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[10px] uppercase font-bold text-neutral-400 tracking-wider">
                ELECTRICAL NETS
              </span>
              <p className="text-xl font-bold text-neutral-900">
                {data.metrics?.nets ?? Object.keys(data.nets || {}).length}
              </p>
            </div>
          </div>

          <div className="p-4 bg-neutral-50 border border-neutral-300 flex items-center gap-3">
            <div className="p-2.5 bg-black text-white rounded-none">
              <Network className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[10px] uppercase font-bold text-neutral-400 tracking-wider">
                CONNECTIONS
              </span>
              <p className="text-xl font-bold text-neutral-900">
                {data.metrics?.connections ?? 0}
              </p>
            </div>
          </div>

          <div className="p-4 bg-neutral-50 border border-neutral-300 flex items-center gap-3">
            <div className="p-2.5 bg-black text-lime-400 rounded-none">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[10px] uppercase font-bold text-neutral-400 tracking-wider">
                CONFIDENCE
              </span>
              <div className="mt-0.5">
                <ConfidenceBadge confidence={data.confidence} size="sm" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* View Mode Selector */}
      <div className="flex justify-center">
        <ViewModeToggle activeTab={activeTab} onChangeTab={setActiveTab} />
      </div>

      {/* 3-Column / Tab Workspace (Fixed clean height to prevent overlapping) */}
      <div className="w-full">
        {activeTab === "split" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[640px]">
            {/* COLUMN 1: Original Image */}
            <div className="bg-white border border-neutral-300 overflow-hidden shadow-sm flex flex-col h-full">
              <div className="px-4 py-2.5 bg-neutral-100 border-b border-neutral-300 font-mono text-xs font-bold text-neutral-900 uppercase tracking-wider">
                Column 1: Original Diagram
              </div>
              <div className="flex-1 bg-neutral-900/5 p-4 flex items-center justify-center overflow-auto">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={imageUrl}
                  alt="Original Schematic"
                  className="max-h-full object-contain border border-neutral-300 shadow bg-white"
                />
              </div>
            </div>

            {/* COLUMN 2: Detection Overlay */}
            <div className="h-full overflow-hidden">
              <DetectionOverlay
                imageUrl={imageUrl}
                data={data}
                selection={selection}
                onSelectComponent={onSelectComponent}
                onSelectTerminal={onSelectTerminal}
                onSelectNet={onSelectNet}
              />
            </div>

            {/* COLUMN 3: Interactive Circuit Graph */}
            <div className="h-full overflow-hidden">
              <CircuitGraphView
                data={data}
                selection={selection}
                onSelectComponent={onSelectComponent}
                onSelectNet={onSelectNet}
              />
            </div>
          </div>
        )}

        {activeTab === "diagram" && (
          <div className="bg-white border border-neutral-300 p-6 shadow-sm flex items-center justify-center min-h-[550px]">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={imageUrl}
              alt="Original Diagram View"
              className="max-h-[600px] object-contain border border-neutral-300 shadow"
            />
          </div>
        )}

        {activeTab === "overlay" && (
          <div className="h-[650px] overflow-hidden">
            <DetectionOverlay
              imageUrl={imageUrl}
              data={data}
              selection={selection}
              onSelectComponent={onSelectComponent}
              onSelectTerminal={onSelectTerminal}
              onSelectNet={onSelectNet}
            />
          </div>
        )}

        {activeTab === "graph" && (
          <div className="h-[650px] overflow-hidden">
            <CircuitGraphView
              data={data}
              selection={selection}
              onSelectComponent={onSelectComponent}
              onSelectNet={onSelectNet}
            />
          </div>
        )}

        {activeTab === "netlist" && (
          <div className="h-[600px] overflow-hidden">
            <NetlistPanel
              data={data}
              selection={selection}
              onSelectNet={onSelectNet}
              onSelectTerminal={onSelectTerminal}
              onSelectComponent={onSelectComponent}
            />
          </div>
        )}
      </div>

      {/* Uncertainty Warnings Banner */}
      {uncertainConnections.length > 0 && (
        <div className="bg-amber-50 border border-amber-300 p-5 shadow-sm font-mono text-xs">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-5 h-5 text-amber-600" />
            <h4 className="font-bold text-amber-950 uppercase">
              Uncertain Connections Flagged ({uncertainConnections.length})
            </h4>
          </div>
          <p className="text-amber-800 mb-3">
            Endpoints with confidence below 70% threshold. Click any entry to inspect its location:
          </p>
          <div className="flex flex-wrap gap-2">
            {uncertainConnections.map((u, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => onSelectTerminal(`${u.compId}.${u.termId}`)}
                className="inline-flex items-center gap-1.5 px-3 py-1 bg-white border border-amber-400 hover:border-black text-amber-950 font-bold shadow-sm transition-all"
              >
                <span>⚠️ {u.compId}.{u.termId} → {u.netId}</span>
                <span className="bg-amber-100 text-amber-900 px-1.5 py-0.5 text-[10px]">
                  {Math.round(u.confidence * 100)}%
                </span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Component Table Below */}
      <ComponentList
        components={data.components}
        selection={selection}
        onSelectComponent={onSelectComponent}
        onSelectNet={onSelectNet}
      />

      {/* Netlist Panel Below */}
      <NetlistPanel
        data={data}
        selection={selection}
        onSelectNet={onSelectNet}
        onSelectTerminal={onSelectTerminal}
        onSelectComponent={onSelectComponent}
      />
    </div>
  );
};
