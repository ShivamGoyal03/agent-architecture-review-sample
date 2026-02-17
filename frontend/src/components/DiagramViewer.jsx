import React, { useEffect, useState, useRef } from "react";
import {
  pngDownloadUrl,
  excalidrawDownloadUrl,
  fetchPngBlobUrl,
  downloadFile,
} from "../api";

function DiagramViewer({ excalidrawFile, runId }) {
  const [Excalidraw, setExcalidraw] = useState(null);
  const [loadError, setLoadError] = useState(false);
  const [pngBlobUrl, setPngBlobUrl] = useState(null);
  const containerRef = useRef(null);

  // Dynamically import @excalidraw/excalidraw
  useEffect(() => {
    let cancelled = false;
    import("@excalidraw/excalidraw")
      .then((mod) => {
        if (!cancelled) {
          setExcalidraw(() => mod.Excalidraw);
        }
      })
      .catch(() => {
        if (!cancelled) setLoadError(true);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  // Fetch PNG as blob URL for reliable preview (works regardless of
  // Content-Disposition headers or proxy configuration)
  useEffect(() => {
    if (!runId) return;
    let cancelled = false;
    fetchPngBlobUrl(runId)
      .then((url) => {
        if (!cancelled) setPngBlobUrl(url);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
      if (pngBlobUrl) URL.revokeObjectURL(pngBlobUrl);
    };
  }, [runId]);

  if (!excalidrawFile) {
    return (
      <div style={{ padding: 24, textAlign: "center", color: "#868e96" }}>
        No diagram data available.
      </div>
    );
  }

  const initialData = {
    elements: excalidrawFile.elements || [],
    appState: {
      viewBackgroundColor: "#ffffff",
      currentItemFontFamily: 1,
      zoom: { value: 1 },
      ...(excalidrawFile.appState || {}),
    },
    scrollToContent: true,
  };

  const pngPreview = pngBlobUrl ? (
    <img
      src={pngBlobUrl}
      alt="Architecture Diagram"
      style={{
        width: "100%",
        height: "100%",
        objectFit: "contain",
        padding: 16,
      }}
    />
  ) : (
    <div className="loading">
      <div className="spinner" />
      Loading diagram preview...
    </div>
  );

  const handleDownloadPng = () => {
    downloadFile(pngDownloadUrl(runId), "architecture.png");
  };

  const handleDownloadExcalidraw = () => {
    downloadFile(excalidrawDownloadUrl(runId), "architecture.excalidraw");
  };

  return (
    <div>
      <div className="diagram-container" ref={containerRef}>
        {loadError ? (
          pngPreview
        ) : Excalidraw ? (
          <Excalidraw
            initialData={initialData}
            viewModeEnabled={false}
            zenModeEnabled={false}
            gridModeEnabled={false}
            theme="light"
          />
        ) : (
          pngPreview
        )}
      </div>

      {runId && (
        <div className="diagram-actions">
          <button className="btn btn-secondary" onClick={handleDownloadPng}>
            Download PNG
          </button>
          <button
            className="btn btn-secondary"
            onClick={handleDownloadExcalidraw}
          >
            Download Excalidraw
          </button>
        </div>
      )}
    </div>
  );
}

export default DiagramViewer;
