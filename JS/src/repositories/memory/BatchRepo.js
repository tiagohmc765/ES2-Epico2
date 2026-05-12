import { BaseRepo } from './BaseRepo.js';

export class BatchRepo extends BaseRepo {
  findByState(state) {
    return this.findAll(b => b.state === state);
  }
}
