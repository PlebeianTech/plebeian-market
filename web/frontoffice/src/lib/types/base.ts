export interface IEntity {
    key: string;

    endpoint: string;

    is_mine: boolean;

    validate: (forSave: boolean) => boolean;
    toJson: () => any;
}
