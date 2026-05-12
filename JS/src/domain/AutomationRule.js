import { AutomationModes } from './enums.js';

export class AutomationRule {
  constructor({
    id,
    batchId,
    parameter,        // 'temperature' | 'humidity' | 'luminosity'
    operator,         // '>' | '<' | '>=' | '<='
    threshold,
    actionType,       // tipo de tarefa a despoletar
    mode = AutomationModes.MANUAL,
    active = true,
    createdAt = new Date(),
    createdBy
  }) {
    this.id = id;
    this.batchId = batchId;
    this.parameter = parameter;
    this.operator = operator;
    this.threshold = threshold;
    this.actionType = actionType;
    this.mode = mode;
    this.active = active;
    this.createdAt = createdAt;
    this.createdBy = createdBy;
  }
}
