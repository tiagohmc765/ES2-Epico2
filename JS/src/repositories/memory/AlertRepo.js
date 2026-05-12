import { BaseRepo } from './BaseRepo.js';

export class AlertRepo extends BaseRepo {
  findByBatch(batchId) {
    return this.findAll(a => a.batchId === batchId);
  }
  findPending() {
    return this.findAll(a => a.status === 'pendente');
  }
}
