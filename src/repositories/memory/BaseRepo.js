/**
 * Repositório in-memory genérico.
 * Mantém os dados num Map e gera ids sequenciais.
 * Permite injeção noutros componentes e fácil substituição por SGBD.
 */
export class BaseRepo {
  constructor() {
    this.items = new Map();
    this.nextId = 1;
  }

  _genId() {
    return this.nextId++;
  }

  create(entity) {
    const id = entity.id ?? this._genId();
    const stored = { ...entity, id };
    this.items.set(id, stored);
    return stored;
  }

  findById(id) {
    return this.items.get(id) ?? null;
  }

  findAll(predicate = null) {
    const all = Array.from(this.items.values());
    return predicate ? all.filter(predicate) : all;
  }

  findOne(predicate) {
    for (const item of this.items.values()) {
      if (predicate(item)) return item;
    }
    return null;
  }

  update(id, patch) {
    const current = this.items.get(id);
    if (!current) return null;
    const updated = { ...current, ...patch, id };
    this.items.set(id, updated);
    return updated;
  }

  delete(id) {
    return this.items.delete(id);
  }

  clear() {
    this.items.clear();
    this.nextId = 1;
  }

  count() {
    return this.items.size;
  }
}
