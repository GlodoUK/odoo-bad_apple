import { FileUploadListRenderer } from "@account/views/file_upload_list/file_upload_list_renderer";

export class TrackListRenderer extends FileUploadListRenderer {
    static template = "bad_odoo.TrackListRenderer";
    static components = {
        ...FileUploadListRenderer.components,
    };
};
