export class AuditEntry {
  constructor({ id, userId, action, resource, resourceId, details = null, timestamp = new Date() }) {
    this.id = id;
    this.userId = userId;
    this.action = action;
    this.resource = resource;
    this.resourceId = resourceId;
    this.details = details;
    this.timestamp = timestamp;
  }
}
