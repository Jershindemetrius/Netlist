"use client";

import React, { useMemo, useCallback } from "react";
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
import { CircuitNode } from "./CircuitNode";
import { CircuitNetNode } from "./CircuitNetNode";
import { Network, Maximize2 } from "lucide-react";

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
  const { nodes: initialNodes, edges: initialEdges } = useMemo(
    () => generateReactFlowGraph(data),
    [data]
  );

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

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

  return (
    <div className="w-full bg-white border border-neutral-200 rounded-xl overflow-hidden shadow-sm flex flex-col h-full min-h-[450px]">
      <div className="flex items-center justify-between px-4 py-2.5 bg-neutral-50 border-b border-neutral-200">
        <div className="flex items-center gap-2">
          <Network className="w-4 h-4 text-black" />
          <span className="font-mono text-xs font-bold text-neutral-900 uppercase tracking-wider">
            Interactive Circuit Graph Canvas
          </span>
        </div>
        <span className="font-mono text-[11px] text-neutral-500">
          Click node to inspect topology
        </span>
      </div>

      <div className="flex-1 relative bg-neutral-50/50">
        <ReactFlow
          nodes={updatedNodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={handleNodeClick}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{ padding: 0.2 }}
          minZoom={0.2}
          maxZoom={2.5}
        >
          <Background variant={BackgroundVariant.Dots} gap={20} size={1} color="#d4d4d4" />
          <Controls className="!bg-white !border-neutral-300 !shadow-sm" />
          <MiniMap
            className="!bg-white !border-neutral-300 !shadow-md rounded-lg"
            nodeColor={(n) => (n.type === "circuitNet" ? "#10b981" : "#000000")}
            zoomable
            pannable
          />
        </ReactFlow>
      </div>
    </div>
  );
};
