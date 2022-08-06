export interface IEntity {
    key: string;

    endpoint: string;

    validate: () => boolean;
    toJson: () => any;
    metaTitle: () => string;
    shortDescription: () => string;
    image: () => string;
}
