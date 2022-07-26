import type { IModel } from "$lib/types/base";

export interface IEditor {
    onSave: () => {};
    onCancel: () => {};
    entity: IModel;
}
