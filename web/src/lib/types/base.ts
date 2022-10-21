export interface IEntity {
    key: string;

    endpoint: string;

    is_mine: boolean;

    validate: () => boolean;
    toJson: () => any;
}
