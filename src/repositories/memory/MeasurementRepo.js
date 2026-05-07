import { BaseRepo } from './BaseRepo.js';

export class MeasurementRepo extends BaseRepo {
  findByBatch(batchId) {
    return this.findAll(m => m.batchId === batchId);
  }
}
