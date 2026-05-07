import { AlertLevels, AlertStatus } from './enums.js';

export class Alert {
  constructor({
    id,
    batchId,
    level,
    message,
    status = AlertStatus.PENDENTE,
    justification = null,
    createdAt = new Date(),
    resolvedAt = null,
    resolvedBy = null
  }) {
    this.id = id;
    this.batchId = batchId;
    this.level = level;
    this.message = message;
    this.status = status;
    this.justification = justification;
    this.createdAt = createdAt;
    this.resolvedAt = resolvedAt;
    this.resolvedBy = resolvedBy;
  }
}

export const JUSTIFICATION_MIN_LENGTH = 10;
export const JUSTIFICATION_MAX_LENGTH = 500;

export const isValidJustification = (text) => {
  if (typeof text !== 'string') return false;
  return text.length >= JUSTIFICATION_MIN_LENGTH && text.length <= JUSTIFICATION_MAX_LENGTH;
};
