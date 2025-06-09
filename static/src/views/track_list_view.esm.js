import {TrackListRenderer} from "./track_list_renderer.esm";
import {fileUploadListView} from "@account/views/file_upload_list/file_upload_list_view";
import {registry} from "@web/core/registry";

export const TrackListView = {
    ...fileUploadListView,
    Renderer: TrackListRenderer,
};

registry.category("views").add("bad_odoo_tracks_list", TrackListView);
