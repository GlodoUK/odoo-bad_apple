import { registry } from "@web/core/registry";
import { fileUploadKanbanView } from "@account/views/file_upload_kanban/file_upload_kanban_view";
import { TrackKanbanRenderer } from "./track_kanban_renderer";

export const TrackKanbanView = {
    ...fileUploadKanbanView,
    Renderer: TrackKanbanRenderer,
};

registry.category("views").add("bad_odoo_tracks_kanban", TrackKanbanView);
