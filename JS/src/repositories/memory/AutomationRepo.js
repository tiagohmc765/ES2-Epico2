import { BaseRepo } from './BaseRepo.js';

export class AutomationRepo extends BaseRepo {
  findByBatch(batchId) {
    return this.findAll(r => r.batchId === batchId);
  }
}
