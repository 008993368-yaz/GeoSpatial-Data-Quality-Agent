import { CalciteBlock } from "@esri/calcite-components-react";
import { FileUploader } from "../components/Upload/FileUploader";

export function UploadPage() {
  return (
    <section className="page-section" aria-labelledby="upload-heading">
      <CalciteBlock heading="Upload dataset" id="upload-heading" expanded collapsible={false}>
        <p className="page-section-description">
          Upload a shapefile or GeoJSON to validate and view on the map.
        </p>
        <FileUploader />
      </CalciteBlock>
    </section>
  );
}
