export interface IEntityBase {
    key: string;
    endpoint: string;
}

export interface IEntity extends IEntityBase {
    is_mine: boolean;

    validate: () => boolean;
    toJson: () => any;
}
