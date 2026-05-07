import { isValidEmail, isValidRole } from '../domain/User.js';

export const buildUsersController = ({ userRepo, hasher, audit }) => ({
  async list(req, res) {
    const users = userRepo.findAll().map(({ passwordHash, ...rest }) => rest);
    res.json(users);
  },

  async getById(req, res) {
    const id = parseInt(req.params.id, 10);
    const user = userRepo.findById(id);
    if (!user) return res.status(404).json({ error: 'User not found' });
    const { passwordHash, ...pub } = user;
    res.json(pub);
  },

  async create(req, res) {
    const { email, password, name, role } = req.body || {};
    if (!isValidEmail(email)) return res.status(422).json({ error: 'Invalid email' });
    if (!isValidRole(role)) return res.status(422).json({ error: 'Invalid role' });
    if (typeof password !== 'string' || password.length < 8) {
      return res.status(422).json({ error: 'Invalid password' });
    }
    if (typeof name !== 'string' || name.trim().length === 0) {
      return res.status(422).json({ error: 'Invalid name' });
    }
    if (userRepo.findByEmail(email)) {
      return res.status(409).json({ error: 'Email already in use' });
    }
    const passwordHash = await hasher.hash(password);
    const created = userRepo.create({
      email: email.trim().toLowerCase(),
      passwordHash,
      name: name.trim(),
      role
    });
    audit.create({ userId: req.user.id, action: 'CREATE', resource: 'users', resourceId: created.id });
    const { passwordHash: _, ...pub } = created;
    res.status(201).json(pub);
  },

  async update(req, res) {
    const id = parseInt(req.params.id, 10);
    const user = userRepo.findById(id);
    if (!user) return res.status(404).json({ error: 'User not found' });
    const patch = {};
    if (req.body?.name !== undefined) patch.name = String(req.body.name).trim();
    if (req.body?.role !== undefined) {
      if (!isValidRole(req.body.role)) return res.status(422).json({ error: 'Invalid role' });
      patch.role = req.body.role;
    }
    const updated = userRepo.update(id, patch);
    audit.create({ userId: req.user.id, action: 'UPDATE', resource: 'users', resourceId: id });
    const { passwordHash, ...pub } = updated;
    res.json(pub);
  },

  async remove(req, res) {
    const id = parseInt(req.params.id, 10);
    if (!userRepo.findById(id)) return res.status(404).json({ error: 'User not found' });
    userRepo.delete(id);
    audit.create({ userId: req.user.id, action: 'DELETE', resource: 'users', resourceId: id });
    res.status(204).send();
  }
});
