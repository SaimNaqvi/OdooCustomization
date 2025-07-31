/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { listView } from "@web/views/list/list_view";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class PhotoGalleryListController extends ListController {
    setup() {
        super.setup();
        this.action = useService("action");
    }

    async openCategoryWizard(category) {
        const context = {
            default_category: category,
            default_partner_id: this.props.context.default_partner_id,
        };

        await this.action.doAction({
             type: "ir.actions.act_window",
            res_model: "fkfp.photo.upload.wizard",
            view_mode: "form",
            views: [[false, "form"]],
            target: "new",
            context: context,
        });
    }

    openBeforeCategory() {
        this.openCategoryWizard("before");
    }

    openFollowUpCategory() {
        this.openCategoryWizard("follow_up");
    }

    openAfterCategory() {
        this.openCategoryWizard("after");
    }
}

registry.category("views").add("photo_gallery_tree", {
    ...listView,
    Controller: PhotoGalleryListController,
    buttonTemplate: "fkfp_manager.ListView.Buttons",
});
