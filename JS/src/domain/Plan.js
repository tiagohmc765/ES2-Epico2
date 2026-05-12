import { ALL_PLAN_TYPES, PlanTypes } from './enums.js';

export class Plan {
  constructor({
    id,
    type,
    herbId,
    tempMin, tempMax,
    humMin, humMax,
    lumMin, lumMax,
    durationDays,
    authorizedBy = null, // user id (Responsavel) when type === pontual
    createdBy,
    createdAt = new Date()
  }) {
    this.id = id;
    this.type = type;
    this.herbId = herbId;
    this.tempMin = tempMin;
    this.tempMax = tempMax;
    this.humMin = humMin;
    this.humMax = humMax;
    this.lumMin = lumMin;
    this.lumMax = lumMax;
    this.durationDays = durationDays;
    this.authorizedBy = authorizedBy;
    this.createdBy = createdBy;
    this.createdAt = createdAt;
  }
}

export const isValidPlanType = (type) => ALL_PLAN_TYPES.includes(type);
export const isPontual = (type) => type === PlanTypes.PONTUAL;

// Limites razoáveis (intervalos exemplo do enunciado)
export const PLAN_LIMITS = Object.freeze({
  TEMP_ABS_MIN: -10, TEMP_ABS_MAX: 50,
  HUM_ABS_MIN: 0,   HUM_ABS_MAX: 100,
  LUM_ABS_MIN: 0,   LUM_ABS_MAX: 100000,
  DURATION_MIN: 1,  DURATION_MAX: 365
});
