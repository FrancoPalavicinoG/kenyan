export interface CheckinCreate {
  energy_level: number      // 1-5
  soreness: number          // 1-5
  perceived_sleep_hours: number  // 0-12
  general_feeling: number   // 1-5
}

export interface AgentInsight {
  resumen: string
  relacion_sueno_readiness: string
  aporte_entrenamientos: string
  tendencia_7_dias: string
  sugerencia_dia: 'fuerte' | 'moderar' | 'descansar'
  sugerencia_detalle: string
  tono: 'positivo' | 'neutro' | 'precaucion'
}

export interface CheckinResponse {
  id: number
  date: string
  energy_level: number
  soreness: number
  perceived_sleep_hours: number
  general_feeling: number
  workout_generated: AgentInsight | null
  agent_message: string | null
  created_at: string
}
