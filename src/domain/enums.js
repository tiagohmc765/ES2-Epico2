// Perfis de utilizador
export const Roles = Object.freeze({
  TECNICO: 'Tecnico',
  RESPONSAVEL: 'Responsavel',
  ADMINISTRADOR: 'Administrador'
});

export const ALL_ROLES = Object.freeze(Object.values(Roles));

// Tipos de plano de cultivo
export const PlanTypes = Object.freeze({
  REGULAR: 'regular',
  EMERGENCIA: 'emergencia',
  PONTUAL: 'pontual'
});

export const ALL_PLAN_TYPES = Object.freeze(Object.values(PlanTypes));

// Estados de lote
export const BatchStates = Object.freeze({
  ATIVO: 'ativo',
  CONCLUIDO: 'concluido',
  COMPROMETIDO: 'comprometido'
});

export const ALL_BATCH_STATES = Object.freeze(Object.values(BatchStates));

// Classificação de alertas
export const AlertLevels = Object.freeze({
  INFORMATIVO: 'Informativo',
  AVISO: 'Aviso',
  CRITICO: 'Critico'
});

export const ALL_ALERT_LEVELS = Object.freeze(Object.values(AlertLevels));

// Estados de alerta
export const AlertStatus = Object.freeze({
  PENDENTE: 'pendente',
  RESOLVIDO: 'resolvido',
  IGNORADO: 'ignorado'
});

// Modos de automação
export const AutomationModes = Object.freeze({
  MANUAL: 'manual',
  AUTOMATICO: 'automatico'
});

// Tipos de tarefas operacionais
export const TaskTypes = Object.freeze({
  REGA: 'rega',
  FERTILIZACAO: 'fertilizacao',
  COLHEITA: 'colheita',
  MONITORIZACAO: 'monitorizacao'
});
