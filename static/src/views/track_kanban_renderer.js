import { FileUploadKanbanRenderer } from "@account/views/file_upload_kanban/file_upload_kanban_renderer";

export class TrackKanbanRenderer extends FileUploadKanbanRenderer {
    static template = "bad_odoo.TrackKanbanRenderer";
    static components = {
        ...FileUploadKanbanRenderer.components,
    };
};
