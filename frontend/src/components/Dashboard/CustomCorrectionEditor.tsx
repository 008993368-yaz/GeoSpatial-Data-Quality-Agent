import { useEffect, useState } from "react";
import { CalciteButton, CalciteLabel, CalciteTextArea } from "@esri/calcite-components-react";

import type { CorrectionOverride, GeometryIssue } from "../../types/api";
import {
  findFeatureInCollection,
  type GeoJsonFeatureCollection,
} from "../../utils/findFeatureInCollection";

export type CustomCorrectionEditorProps = {
  datasetId: string;
  issue: GeometryIssue;
  savedOverride: CorrectionOverride | undefined;
  onSave: (override: CorrectionOverride) => void;
  onClear: () => void;
  disabled?: boolean;
};

function isGeometryIssueType(type: string): boolean {
  return !type.startsWith("attribute_") && !type.startsWith("topology_");
}

export function CustomCorrectionEditor({
  datasetId,
  issue,
  savedOverride,
  onSave,
  onClear,
  disabled = false,
}: CustomCorrectionEditorProps) {
  const [geometryWkt, setGeometryWkt] = useState(savedOverride?.geometry_wkt ?? "");
  const [attributesJson, setAttributesJson] = useState("");
  const [parseError, setParseError] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  const showGeometry = isGeometryIssueType(issue.type || "");

  useEffect(() => {
    setGeometryWkt(savedOverride?.geometry_wkt ?? "");
    if (savedOverride?.attributes) {
      setAttributesJson(JSON.stringify(savedOverride.attributes, null, 2));
    }
  }, [savedOverride]);

  useEffect(() => {
    if (savedOverride?.attributes || issue.feature_id === undefined || issue.feature_id === null) {
      return;
    }
    let cancelled = false;
    setLoadError(null);
    void (async () => {
      try {
        const res = await fetch(`/api/v1/datasets/${datasetId}/geojson`);
        if (!res.ok) return;
        const collection = (await res.json()) as GeoJsonFeatureCollection;
        const feature = findFeatureInCollection(collection, issue.feature_id);
        if (cancelled || !feature?.properties) return;
        const { geometry: _geom, ...rest } = feature.properties as Record<string, unknown>;
        void _geom;
        if (Object.keys(rest).length > 0) {
          setAttributesJson(JSON.stringify(rest, null, 2));
        }
      } catch {
        if (!cancelled) setLoadError("Could not load current feature attributes.");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [datasetId, issue.feature_id, savedOverride?.attributes]);

  function handleSave() {
    setParseError(null);
    let attributes: Record<string, unknown> | undefined;
    const trimmedAttrs = attributesJson.trim();
    if (trimmedAttrs) {
      try {
        const parsed = JSON.parse(trimmedAttrs) as unknown;
        if (parsed === null || typeof parsed !== "object" || Array.isArray(parsed)) {
          setParseError("Attributes must be a JSON object (e.g. {\"name\": \"value\"}).");
          return;
        }
        attributes = parsed as Record<string, unknown>;
      } catch {
        setParseError("Attributes must be valid JSON.");
        return;
      }
    }

    const trimmedWkt = geometryWkt.trim();
    if (!trimmedWkt && !attributes) {
      setParseError("Enter geometry WKT and/or attribute JSON before saving.");
      return;
    }

    onSave({
      feature_id: issue.feature_id,
      ...(trimmedWkt ? { geometry_wkt: trimmedWkt } : {}),
      ...(attributes ? { attributes } : {}),
    });
  }

  return (
    <div className="custom-correction-editor">
      <p className="custom-correction-editor__intro">
        Edit values below, then save. Overrides are sent when you apply corrections. There is no
        interactive map editor — use WKT for geometry and JSON for attributes.
      </p>
      {loadError && <p className="custom-correction-editor__error">{loadError}</p>}
      {showGeometry && (
        <CalciteLabel>
          Geometry (WKT)
          <CalciteTextArea
            value={geometryWkt}
            placeholder='e.g. POINT (-122.42 37.78) or POLYGON ((...))'
            rows={4}
            disabled={disabled}
            onCalciteTextAreaInput={(event) => {
              setGeometryWkt((event.target as HTMLCalciteTextAreaElement).value ?? "");
            }}
          />
        </CalciteLabel>
      )}
      <CalciteLabel>
        Attributes (JSON object)
        <CalciteTextArea
          value={attributesJson}
          placeholder='{"name": "Corrected name"}'
          rows={5}
          disabled={disabled}
          onCalciteTextAreaInput={(event) => {
            setAttributesJson((event.target as HTMLCalciteTextAreaElement).value ?? "");
          }}
        />
      </CalciteLabel>
      {parseError && <p className="custom-correction-editor__error">{parseError}</p>}
      {savedOverride && (
        <p className="custom-correction-editor__saved" role="status">
          Custom fix saved for this issue.
        </p>
      )}
      <div className="custom-correction-editor__actions">
        <CalciteButton kind="brand" onClick={handleSave} disabled={disabled}>
          Save custom fix
        </CalciteButton>
        {savedOverride && (
          <CalciteButton appearance="outline" kind="neutral" onClick={onClear} disabled={disabled}>
            Clear saved fix
          </CalciteButton>
        )}
      </div>
    </div>
  );
}
