import { BaseRepo } from './BaseRepo.js';

export class HerbRepo extends BaseRepo {
  findByName(name) {
    if (!name) return null;
    const n = name.toLowerCase().trim();
    return this.findOne(h => h.name.toLowerCase() === n);
  }
}
