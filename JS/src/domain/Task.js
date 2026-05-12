import { TaskTypes } from './enums.js';

export class OperationalTask {
  constructor({
    id,
    batchId,
    type,
    description = '',
    scheduledFor,
    executedAt = null,
    executedBy = null,
    createdAt = new Date()
  }) {
    this.id = id;
    this.batchId = batchId;
    this.type = type;
    this.description = description;
    this.scheduledFor = scheduledFor;
    this.executedAt = executedAt;
    this.executedBy = executedBy;
    this.createdAt = createdAt;
  }
}

export const isValidTaskType = (t) => Object.values(TaskTypes).includes(t);
