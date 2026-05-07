import { ALL_BATCH_STATES, BatchStates } from './enums.js';

export class Batch {
  constructor({
    id,
    herbId,
    planId = null,
    state = BatchStates.ATIVO,
    startDate = new Date(),
    endDate = null,
    initialQuantity = 0,
    losses = 0,
    splits = [],
    createdBy,
    createdAt = new Date()
  }) {
    this.id = id;
    this.herbId = herbId;
    this.planId = planId;
    this.state = state;
    this.startDate = startDate;
    this.endDate = endDate;
    this.initialQuantity = initialQuantity;
    this.losses = losses;
    this.splits = splits;
    this.createdBy = createdBy;
    this.createdAt = createdAt;
  }
}

export const isValidBatchState = (state) => ALL_BATCH_STATES.includes(state);

// Transições permitidas
const allowedTransitions = {
  [BatchStates.ATIVO]: [BatchStates.CONCLUIDO, BatchStates.COMPROMETIDO],
  [BatchStates.CONCLUIDO]: [],
  [BatchStates.COMPROMETIDO]: []
};

export const isAllowedTransition = (from, to) => {
  if (!isValidBatchState(from) || !isValidBatchState(to)) return false;
  return allowedTransitions[from].includes(to);
};
