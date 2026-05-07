import { BaseRepo } from './BaseRepo.js';

export class AuditRepo extends BaseRepo {
  findByUser(userId) {
    return this.findAll(e => e.userId === userId);
  }
  findByResource(resource, resourceId) {
    return this.findAll(e => e.resource === resource && e.resourceId === resourceId);
  }
}
