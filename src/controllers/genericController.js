/**
 * Controller CRUD genérico para endpoints ainda em fase de esqueleto.
 * Endpoints reais (com regras de negócio completas) serão desenvolvidos
 * nas sprints seguintes; aqui já validamos auth, RBAC e estrutura HTTP.
 */
export const buildGenericController = ({ repo, resourceName, audit }) => ({
  list(req, res) {
    res.json(repo.findAll());
  },
  get(req, res) {
    const id = parseInt(req.params.id, 10);
    const item = repo.findById(id);
    if (!item) return res.status(404).json({ error: `${resourceName} not found` });
    res.json(item);
  },
  create(req, res) {
    const created = repo.create({ ...(req.body || {}), createdBy: req.user?.id });
    audit?.create({ userId: req.user.id, action: 'CREATE', resource: resourceName, resourceId: created.id });
    res.status(201).json(created);
  },
  update(req, res) {
    const id = parseInt(req.params.id, 10);
    if (!repo.findById(id)) return res.status(404).json({ error: `${resourceName} not found` });
    const updated = repo.update(id, req.body || {});
    audit?.create({ userId: req.user.id, action: 'UPDATE', resource: resourceName, resourceId: id });
    res.json(updated);
  },
  remove(req, res) {
    const id = parseInt(req.params.id, 10);
    if (!repo.findById(id)) return res.status(404).json({ error: `${resourceName} not found` });
    repo.delete(id);
    audit?.create({ userId: req.user.id, action: 'DELETE', resource: resourceName, resourceId: id });
    res.status(204).send();
  }
});
