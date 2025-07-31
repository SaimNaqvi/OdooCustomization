/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { listView } from "@web/views/list/list_view";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class DocumentListController extends ListController {
    setup() {
        super.setup();
        this.action = useService("action");
    }

    async openDocumentWizard(docType) {
        const context = {
            default_partner_id: this.props.context.default_partner_id,
            default_document_type: docType,
        };

        await this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "fkfp.document.upload.wizard",
            view_mode: "form",
            views: [[false, "form"]],
            target: "new",
            context: context,
        });
    }

    openNicFront() {
        this.openDocumentWizard("nic_front");
    }
    openNicBack() {
        this.openDocumentWizard("nic_back");
    }
    openStampPaper() {
        this.openDocumentWizard("stamp_paper");
    }
    openDas() {
        this.openDocumentWizard("das");
    }
    openOther() {
        this.openDocumentWizard("other");
    }
}

registry.category("views").add("document_gallery_tree", {
    ...listView,
    Controller: DocumentListController,
    buttonTemplate: "fkfp_manager.DocumentListView.Buttons",
});
