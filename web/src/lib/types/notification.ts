export interface NotificationAction {
    action: string;
    description: string;
}

export interface UserNotification {
    notificationType: string;
    notificationTypeDescription: string;
    action: NotificationAction;
    availableActions: NotificationAction[];
}

export function fromJson(json: any) {
    return {
        notificationType: <string>json.notification_type,
        notificationTypeDescription: <string>json.notification_type_description,
        action: <NotificationAction>json.action,
        availableActions: <NotificationAction[]>json.available_actions,
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