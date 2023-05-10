export interface NotificationAction {
    action: string;
    description: string;
}

export interface UserNotification {
    notificationType: string;
    notificationTypeDescription: string;
    action: string;
    availableActions: NotificationAction[];
    isDefault: boolean;
}

export function fromJson(json: any): UserNotification {
    return {
        notificationType: <string>json.notification_type,
        notificationTypeDescription: <string>json.notification_type_description,
        action: <string>json.action,
        availableActions: <NotificationAction[]>json.available_actions,
        isDefault: <boolean>json.is_default,
    }
}

export class PostUserNotification {
    notificationType: string;
    action: string;

    public constructor(notificationType: string, action: string) {
        this.notificationType = notificationType;
        this.action = action;
    }

    public toJson() {
        return {
            notification_type: this.notificationType,
            action: this.action,
        };
    }
}