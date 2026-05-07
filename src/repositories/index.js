import { UserRepo } from './memory/UserRepo.js';
import { HerbRepo } from './memory/HerbRepo.js';
import { PlanRepo } from './memory/PlanRepo.js';
import { BatchRepo } from './memory/BatchRepo.js';
import { TaskRepo } from './memory/TaskRepo.js';
import { MeasurementRepo } from './memory/MeasurementRepo.js';
import { AlertRepo } from './memory/AlertRepo.js';
import { AutomationRepo } from './memory/AutomationRepo.js';
import { AuditRepo } from './memory/AuditRepo.js';

/**
 * Cria o conjunto completo de repositórios in-memory.
 * Função fábrica - permite criar instâncias isoladas para testes.
 */
export const createRepositories = () => ({
  users: new UserRepo(),
  herbs: new HerbRepo(),
  plans: new PlanRepo(),
  batches: new BatchRepo(),
  tasks: new TaskRepo(),
  measurements: new MeasurementRepo(),
  alerts: new AlertRepo(),
  automation: new AutomationRepo(),
  audit: new AuditRepo()
});
