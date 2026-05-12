import { BaseRepo } from './BaseRepo.js';

export class UserRepo extends BaseRepo {
  findByEmail(email) {
    if (!email) return null;
    const normalized = email.toLowerCase().trim();
    return this.findOne(u => u.email.toLowerCase() === normalized);
  }
}
