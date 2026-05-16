export type GeoJsonFeature = {
  type: "Feature";
  id?: string | number;
  properties?: Record<string, unknown> | null;
  geometry?: unknown;
};

export type GeoJsonFeatureCollection = {
  type: "FeatureCollection";
  features: GeoJsonFeature[];
};

/** Locate a feature in a GeoJSON FeatureCollection by feature_id from validation issues. */
export function findFeatureInCollection(
  collection: GeoJsonFeatureCollection,
  featureId: unknown,
): GeoJsonFeature | null {
  if (!collection?.features?.length || featureId === undefined || featureId === null) {
    return null;
  }
  const idStr = String(featureId);
  for (const feature of collection.features) {
    const props = feature.properties ?? {};
    if (props.id !== undefined && String(props.id) === idStr) {
      return feature;
    }
    if (feature.id !== undefined && String(feature.id) === idStr) {
      return feature;
    }
  }
  const asIndex = Number(featureId);
  if (!Number.isNaN(asIndex) && asIndex >= 0 && asIndex < collection.features.length) {
    return collection.features[asIndex] ?? null;
  }
  return null;
}
