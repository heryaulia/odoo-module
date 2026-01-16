/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { FormLabel } from "@web/views/form/form_label";
import { ListRenderer } from "@web/views/list/list_renderer";

// Patch ListRenderer for list/tree view column header tooltips
patch(ListRenderer.prototype, {
    makeTooltip(column) {
        console.log('[Technical Debug] ListRenderer.makeTooltip called');
        console.log('[Technical Debug] column:', column);
        console.log('[Technical Debug] this.fields:', this.fields);

        const result = super.makeTooltip(column);

        console.log('[Technical Debug] result:', result);
        console.log('[Technical Debug] odoo.debug:', odoo.debug);

        // Only modify in debug mode
        if (!odoo.debug) {
            console.log('[Technical Debug] Debug mode OFF');
            return result;
        }

        const parsedInfo = JSON.parse(result);
        const field = this.fields[column.name];

        console.log('[Technical Debug] field:', field);
        console.log('[Technical Debug] field.modules:', field?.modules);

        // Add module information if available
        if (field && field.modules) {
            console.log('[Technical Debug] Adding modules:', field.modules);
            parsedInfo.field = parsedInfo.field || {};
            parsedInfo.field.modules = field.modules;
        }

        return JSON.stringify(parsedInfo);
    }
});

// Patch FormLabel for form view tooltips
patch(FormLabel.prototype, {
    get tooltipInfo() {
        const result = super.tooltipInfo;

        // Only modify in debug mode
        if (!odoo.debug) {
            return result;
        }

        const parsedInfo = JSON.parse(result);
        const field = this.props.record.fields[this.props.fieldName];

        // Add module information if available
        if (field && field.modules) {
            parsedInfo.field = parsedInfo.field || {};
            parsedInfo.field.modules = field.modules;
        }

        return JSON.stringify(parsedInfo);
    }
});
