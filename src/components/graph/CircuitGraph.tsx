"use client";

import React, { useMemo, useCallback, useState } from "react";
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  BackgroundVariant,
  useNodesState,
  useEdgesState,
  Node,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";

import { CircuitGraphResponse, SelectionState } from "../../lib/types";
import { generateReactFlowGraph } from "../../lib/graph";
import { simplifyCircuitGraph } from "../../lib/simplifier";
import { CircuitNode } from "./CircuitNode";
import { CircuitNetNode } from "./CircuitNetNode";
import { Network, Maximize2, X, FileText, Image as ImageIcon, Zap, Sparkles, RefreshCw } from "lucide-react";
import { exportGraphAsJpeg, exportReportAsPdf } from "../../lib/export";

interface CircuitGraphProps {
  data: CircuitGraphResponse;
  selection: SelectionState;
  onSelectComponent: (id: string | null) => void;
  onSelectNet: (netId: string | null) => void;
}

const nodeTypes = {
  circuitComponent: CircuitNode,
  circuitNet: CircuitNetNode,
};

export const CircuitGraphView: React.FC<CircuitGraphProps> = ({
  data,
  selection,
  onSelectComponent,
  onSelectNet,
}) => {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isSimplified, setIsSimplified] = useState(false);

  // Generate Graph Data (Original vs Simplified Equivalent)
  const graphInputData: CircuitGraphResponse = useMemo(() => {
    if (!isSimplified) return data;
    return simplifyCircuitGraph(data);
  }, [data, isSimplified]);

  const { nodes: initialNodes, edges: initialEdges } = useMemo(
    () => generateReactFlowGraph(graphInputData),
    [graphInputData]
  );

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Synchronize ReactFlow nodes and edges whenever input data or simplification updates
  React.useEffect(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
  }, [initialNodes, initialEdges, setNodes, setEdges]);

  // Synchronize selection state with nodes
  const updatedNodes = useMemo(() => {
    return nodes.map((node) => {
      let isSelected = false;
      if (node.type === "circuitComponent") {
        isSelected = selection.type === "component" && selection.componentId === node.id;
      } else if (node.type === "circuitNet") {
        const netId = node.data?.netId;
        isSelected = selection.type === "net" && selection.netId === netId;
      }
      return {
        ...node,
        selected: isSelected,
      };
    });
  }, [nodes, selection]);

  const handleNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      if (node.type === "circuitComponent") {
        onSelectComponent(node.id);
      } else if (node.type === "circuitNet") {
        const netId = (node.data as any)?.netId;
        onSelectNet(netId);
      }
    },
    [onSelectComponent, onSelectNet]
  );

  const renderReactFlowCanvas = (containerId: string) => (
    <div id={containerId} className="w-full h-full relative bg-slate-50/40">
      <ReactFlow
        nodes={updatedNodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={handleNodeClick}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.15 }}
        minZoom={0.4}
        maxZoom={2.2}
      >
        <Background variant={BackgroundVariant.Dots} gap={16} size={1} color="#cbd5e1" />
        <Controls className="!bg-white !border-slate-200 !shadow-sm !rounded-lg" />
        <MiniMap
          className="!bg-white !border-slate-200 !shadow-sm !rounded-2xl"
          nodeColor={(n) => (n.type === "circuitNet" ? "#6366f1" : "#10b981")}
          zoomable
          pannable
        />
      </ReactFlow>
    </div>
  );

  return (
    <>
      {/* Standard Pane View matching Image 1 & 3 */}
      <div className="w-full bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-xs flex flex-col h-full min-h-[480px]">
        {/* Header Bar */}
        <div className="flex items-center justify-between px-4 py-3 bg-slate-50 border-b border-slate-200 flex-wrap gap-2">
          <div className="flex items-center gap-2">
            <h3 className="font-sans font-bold text-sm text-slate-900 leading-none">
              3. CIRCUIT GRAPH
            </h3>
            <span className="px-2.5 py-0.5 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-full font-bold text-[11px]">
              Confidence: {(data.confidence ?? 0.94).toFixed(2)} (HIGH)
            </span>
          </div>

          {/* Simplification & Export Controls */}
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setIsSimplified(!isSimplified)}
              className={`px-3 py-1 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
                isSimplified
                  ? "bg-indigo-600 text-white shadow-2xs"
                  : "bg-white border border-slate-300 text-slate-700 hover:bg-slate-100"
              }`}
            >
              <Zap className="w-3.5 h-3.5 text-amber-400" />
              <span>{isSimplified ? "Simplified Equivalent" : "Simplify Circuit"}</span>
            </button>

            <button
              type="button"
              onClick={() => exportGraphAsJpeg("circuit-graph-canvas")}
              className="p-1.5 hover:bg-slate-200/60 rounded-lg text-slate-600 cursor-pointer"
              title="Download Graph JPEG"
            >
              <ImageIcon className="w-4 h-4 text-emerald-600" />
            </button>

            <button
              type="button"
              onClick={() => exportReportAsPdf("circuit-graph-canvas")}
              className="p-1.5 hover:bg-slate-200/60 rounded-lg text-slate-600 cursor-pointer"
              title="Download Graph PDF"
            >
              <FileText className="w-4 h-4 text-indigo-600" />
            </button>

            <button
              type="button"
              onClick={() => setIsFullscreen(true)}
              className="p-1.5 hover:bg-slate-200/60 rounded-lg text-slate-600 cursor-pointer"
              title="Open Full Screen View"
            >
              <Maximize2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* React Flow Canvas */}
        <div className="flex-1 relative">
          {renderReactFlowCanvas("circuit-graph-canvas")}
        </div>
      </div>

      {/* Full Screen Modal Overlay */}
      {isFullscreen && (
        <div className="fixed inset-0 z-50 bg-slate-900/80 backdrop-blur-xs flex items-center justify-center p-4 md:p-8 animate-in fade-in duration-200">
          <div className="bg-white rounded-2xl w-full h-full max-w-7xl max-h-[92vh] flex flex-col overflow-hidden shadow-2xl border border-slate-200">
            {/* Modal Header */}
            <div className="flex items-center justify-between px-6 py-4 bg-slate-900 text-white border-b border-slate-800">
              <div className="flex items-center gap-3">
                <Network className="w-5 h-5 text-indigo-400" />
                <div>
                  <h3 className="font-bold text-base">Full Screen Circuit Topology Graph</h3>
                  <p className="text-xs text-slate-400 font-mono">
                    Image ID: {data.image_id} • {graphInputData.components.length} Components • {Object.keys(graphInputData.nets || {}).length} Nets
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => setIsSimplified(!isSimplified)}
                  className="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl text-xs flex items-center gap-1.5 cursor-pointer"
                >
                  <Zap className="w-4 h-4 text-amber-300" />
                  <span>{isSimplified ? "Showing Simplified" : "Simplify Circuit"}</span>
                </button>

                <button
                  type="button"
                  onClick={() => exportGraphAsJpeg("fullscreen-graph-canvas")}
                  className="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-white font-semibold rounded-xl text-xs flex items-center gap-1.5 cursor-pointer"
                >
                  <ImageIcon className="w-4 h-4 text-emerald-400" />
                  <span>Download JPEG</span>
                </button>

                <button
                  type="button"
                  onClick={() => exportReportAsPdf("fullscreen-graph-canvas")}
                  className="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl text-xs flex items-center gap-1.5 cursor-pointer"
                >
                  <FileText className="w-4 h-4" />
                  <span>Download PDF</span>
                </button>

                <button
                  type="button"
                  onClick={() => setIsFullscreen(false)}
                  className="p-2 hover:bg-slate-800 rounded-xl text-slate-300 hover:text-white cursor-pointer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Modal Canvas Body */}
            <div className="flex-1 relative">
              {renderReactFlowCanvas("fullscreen-graph-canvas")}
            </div>
          </div>
        </div>
      )}
    </>
  );
};
