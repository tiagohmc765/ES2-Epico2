import { BaseRepo } from './BaseRepo.js';

export class PlanRepo extends BaseRepo {
  findByHerb(herbId) {
    return this.findAll(p => p.herbId === herbId);
  }
}
