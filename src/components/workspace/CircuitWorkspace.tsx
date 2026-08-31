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
  FileCode,
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
      <div className="bg-white border border-neutral-200 rounded-xl p-6 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-4 pb-6 border-b border-neutral-200">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-mono font-bold text-neutral-900">
                Circuit Reconstruction Results
              </h2>
              <span className="font-mono text-xs bg-neutral-100 border border-neutral-300 text-neutral-800 px-2.5 py-0.5 rounded font-semibold">
                ID: {data.image_id}
              </span>
            </div>
            <p className="font-mono text-xs text-neutral-500 mt-1">
              Hand-drawn diagram converted to canonical CircuitGraph and SPICE netlist.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              type="button"
              onClick={() => exportCircuitJson(data)}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-mono font-bold border border-neutral-300 bg-white hover:bg-neutral-100 text-neutral-900 rounded-lg shadow-sm"
            >
              <Download className="w-4 h-4" />
              <span>Export JSON</span>
            </button>
            <button
              type="button"
              onClick={() => exportSpiceNetlist(data)}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-mono font-bold bg-black hover:bg-neutral-800 text-white rounded-lg shadow-sm"
            >
              <Download className="w-4 h-4" />
              <span>Export Netlist</span>
            </button>
            <button
              type="button"
              onClick={onReset}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-mono font-bold border border-neutral-300 bg-neutral-50 hover:bg-neutral-100 text-neutral-700 rounded-lg"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Reset & Process Another</span>
            </button>
          </div>
        </div>

        {/* Metric Cards Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6">
          <div className="p-4 bg-neutral-50 border border-neutral-200 rounded-xl flex items-center gap-3">
            <div className="p-2.5 bg-black text-white rounded-lg shadow-sm">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <span className="font-mono text-[10px] uppercase font-bold text-neutral-400">
                COMPONENTS
              </span>
              <p className="font-mono text-xl font-bold text-neutral-900">
                {data.metrics?.components ?? data.components.length}
              </p>
            </div>
          </div>

          <div className="p-4 bg-neutral-50 border border-neutral-200 rounded-xl flex items-center gap-3">
            <div className="p-2.5 bg-black text-white rounded-lg shadow-sm">
              <Zap className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <span className="font-mono text-[10px] uppercase font-bold text-neutral-400">
                ELECTRICAL NETS
              </span>
              <p className="font-mono text-xl font-bold text-neutral-900">
                {data.metrics?.nets ?? Object.keys(data.nets || {}).length}
              </p>
            </div>
          </div>

          <div className="p-4 bg-neutral-50 border border-neutral-200 rounded-xl flex items-center gap-3">
            <div className="p-2.5 bg-black text-white rounded-lg shadow-sm">
              <Network className="w-5 h-5" />
            </div>
            <div>
              <span className="font-mono text-[10px] uppercase font-bold text-neutral-400">
                CONNECTIONS
              </span>
              <p className="font-mono text-xl font-bold text-neutral-900">
                {data.metrics?.connections ?? 0}
              </p>
            </div>
          </div>

          <div className="p-4 bg-neutral-50 border border-neutral-200 rounded-xl flex items-center gap-3">
            <div className="p-2.5 bg-black text-white rounded-lg shadow-sm">
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <span className="font-mono text-[10px] uppercase font-bold text-neutral-400">
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

      {/* 3-Column / Tab Workspace */}
      <div className="w-full min-h-[550px]">
        {activeTab === "split" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[600px]">
            {/* COLUMN 1: Original Image */}
            <div className="bg-white border border-neutral-200 rounded-xl overflow-hidden shadow-sm flex flex-col h-full">
              <div className="px-4 py-2.5 bg-neutral-50 border-b border-neutral-200 font-mono text-xs font-bold text-neutral-900 uppercase">
                Column 1: Original Circuit Photograph
              </div>
              <div className="flex-1 bg-neutral-900/5 p-4 flex items-center justify-center overflow-auto">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={imageUrl}
                  alt="Original Hand-drawn Circuit"
                  className="max-h-[500px] object-contain rounded border border-neutral-200 shadow bg-white"
                />
              </div>
            </div>

            {/* COLUMN 2: Detection Overlay */}
            <div className="h-full">
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
            <div className="h-full">
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
          <div className="bg-white border border-neutral-200 rounded-xl p-6 shadow-sm flex items-center justify-center min-h-[500px]">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={imageUrl}
              alt="Original Diagram"
              className="max-h-[600px] object-contain rounded-lg border border-neutral-300 shadow"
            />
          </div>
        )}

        {activeTab === "overlay" && (
          <div className="h-[600px]">
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
          <div className="h-[600px]">
            <CircuitGraphView
              data={data}
              selection={selection}
              onSelectComponent={onSelectComponent}
              onSelectNet={onSelectNet}
            />
          </div>
        )}

        {activeTab === "netlist" && (
          <div className="h-[550px]">
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

      {/* Uncertainty Warnings Section */}
      {uncertainConnections.length > 0 && (
        <div className="bg-amber-50/80 border border-amber-300 rounded-xl p-5 shadow-sm">
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle className="w-5 h-5 text-amber-600" />
            <h4 className="font-mono text-sm font-bold text-amber-900">
              Uncertain Connections Identified ({uncertainConnections.length})
            </h4>
          </div>
          <p className="font-mono text-xs text-amber-800 mb-3">
            The computer vision model flagged the following connection endpoints with confidence below threshold (70%). Click any entry to inspect its exact image region.
          </p>
          <div className="flex flex-wrap gap-2 font-mono text-xs">
            {uncertainConnections.map((u, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => onSelectTerminal(`${u.compId}.${u.termId}`)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white border border-amber-300 hover:border-black rounded-lg text-amber-900 shadow-sm font-bold transition-all hover:scale-105"
              >
                <span>⚠️ {u.compId}.{u.termId} → {u.netId}</span>
                <span className="bg-amber-100 text-amber-900 text-[10px] px-1.5 py-0.5 rounded">
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
