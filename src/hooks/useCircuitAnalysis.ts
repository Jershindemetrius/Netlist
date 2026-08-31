/**
 * React Hook for Circuit Image Upload, Analysis Execution, and Bidirectional Selection State
 */

import { useState, useCallback, useMemo } from "react";
import {
  CircuitGraphResponse,
  ProcessingStep,
  SelectionState,
  ComponentData,
  TerminalData,
} from "../lib/types";
import { analyzeCircuitImage, loadDemoCircuit } from "../lib/api";

const INITIAL_STEPS: ProcessingStep[] = [
  { id: 1, label: "Image Preprocessing", detail: "Denoising & adaptive thresholding", status: "pending" },
  { id: 2, label: "Component Detection", detail: "YOLO11s symbol localization", status: "pending" },
  { id: 3, label: "Tracing Wires", detail: "Morphological skeletonization", status: "pending" },
  { id: 4, label: "Estimating Terminals", detail: "Class-aware port snapping", status: "pending" },
  { id: 5, label: "Building Circuit Graph", detail: "Disjoint Set Union net clustering", status: "pending" },
  { id: 6, label: "Validating Topology", detail: "Electrical rule check & GED score", status: "pending" },
];

export function useCircuitAnalysis() {
  const [imageFile, setImageFile] = useState<File | Blob | null>(null);
  const [imagePreviewUrl, setImagePreviewUrl] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [processingSteps, setProcessingSteps] = useState<ProcessingStep[]>(INITIAL_STEPS);
  const [result, setResult] = useState<CircuitGraphResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [selection, setSelection] = useState<SelectionState>({
    type: "none",
    id: null,
    componentId: null,
    netId: null,
    terminalId: null,
  });

  const handleImageSelect = useCallback((file: File) => {
    setImageFile(file);
    const url = URL.createObjectURL(file);
    setImagePreviewUrl(url);
    setResult(null);
    setError(null);
    setSelection({ type: "none", id: null });
  }, []);

  const runAnalysis = useCallback(async () => {
    if (!imageFile) return;

    setIsAnalyzing(true);
    setError(null);
    setProcessingSteps(
      INITIAL_STEPS.map((s, idx) => ({
        ...s,
        status: idx === 0 ? "processing" : "pending",
      }))
    );

    try {
      const response = await analyzeCircuitImage(imageFile, (stepNum) => {
        setCurrentStep(stepNum);
        setProcessingSteps((prev) =>
          prev.map((step) => {
            if (step.id < stepNum) return { ...step, status: "completed" };
            if (step.id === stepNum) return { ...step, status: "processing" };
            return { ...step, status: "pending" };
          })
        );
      });

      setProcessingSteps((prev) => prev.map((s) => ({ ...s, status: "completed" })));
      setResult(response);
    } catch (err: any) {
      setError(err.message || "Failed to analyze circuit image.");
      setProcessingSteps((prev) =>
        prev.map((s) => (s.status === "processing" ? { ...s, status: "error" } : s))
      );
    } finally {
      setIsAnalyzing(false);
    }
  }, [imageFile]);

  const loadDemo = useCallback(async () => {
    setIsAnalyzing(true);
    setError(null);
    setImagePreviewUrl("/demo/sample_circuit.png");

    try {
      const demoResult = await loadDemoCircuit();
      setResult(demoResult);
      setProcessingSteps(INITIAL_STEPS.map((s) => ({ ...s, status: "completed" })));
    } catch (err: any) {
      setError("Failed to load demo circuit.");
    } finally {
      setIsAnalyzing(false);
    }
  }, []);

  const reset = useCallback(() => {
    setImageFile(null);
    if (imagePreviewUrl && !imagePreviewUrl.includes("/demo/")) {
      URL.revokeObjectURL(imagePreviewUrl);
    }
    setImagePreviewUrl(null);
    setIsAnalyzing(false);
    setResult(null);
    setError(null);
    setSelection({ type: "none", id: null });
    setProcessingSteps(INITIAL_STEPS);
  }, [imagePreviewUrl]);

  // Selection Action Handlers
  const selectComponent = useCallback((id: string | null) => {
    if (!id) {
      setSelection({ type: "none", id: null });
      return;
    }
    setSelection({
      type: "component",
      id,
      componentId: id,
    });
  }, []);

  const selectTerminal = useCallback((terminalRef: string | null) => {
    if (!terminalRef) {
      setSelection({ type: "none", id: null });
      return;
    }
    const parts = terminalRef.split(".");
    const compId = parts[0];
    setSelection({
      type: "terminal",
      id: terminalRef,
      componentId: compId,
      terminalId: terminalRef,
    });
  }, []);

  const selectNet = useCallback((netId: string | null) => {
    if (!netId) {
      setSelection({ type: "none", id: null });
      return;
    }
    setSelection({
      type: "net",
      id: netId,
      netId: netId,
    });
  }, []);

  // Compute uncertain connections (< 0.70 confidence)
  const uncertainConnections = useMemo(() => {
    if (!result) return [];
    const list: { compId: string; termId: string; netId: string; confidence: number }[] = [];
    
    result.components.forEach((comp) => {
      comp.terminals.forEach((term) => {
        const conf = term.confidence ?? comp.confidence;
        if (conf < 0.70 && term.net) {
          list.push({
            compId: comp.id,
            termId: term.id,
            netId: term.net,
            confidence: conf,
          });
        }
      });
    });
    return list;
  }, [result]);

  return {
    imageFile,
    imagePreviewUrl,
    isAnalyzing,
    currentStep,
    processingSteps,
    result,
    error,
    selection,
    uncertainConnections,
    handleImageSelect,
    runAnalysis,
    loadDemo,
    reset,
    selectComponent,
    selectTerminal,
    selectNet,
  };
}
