import { BaseRepo } from './BaseRepo.js';

export class TaskRepo extends BaseRepo {
  findByBatch(batchId) {
    return this.findAll(t => t.batchId === batchId);
  }
}
