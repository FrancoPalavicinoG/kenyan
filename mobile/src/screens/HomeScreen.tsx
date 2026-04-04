import { useQuery } from '@tanstack/react-query'
import { StackNavigationProp } from '@react-navigation/stack'
import React, { useRef, useState } from 'react'
import {
  ActivityIndicator,
  Animated,
  StyleSheet,
  Text,
  TouchableWithoutFeedback,
  View,
  useWindowDimensions,
} from 'react-native'
import { SafeAreaView } from 'react-native-safe-area-context'
import { RootStackParamList } from '../../App'
import ProgressBars from '../components/ProgressBars'
import StorySlide from '../components/StorySlide'
import { checkinApi, metricsApi } from '../api'
import { colors, radius, spacing, typography } from '../theme'

type HomeScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Home'>

interface Props {
  navigation: HomeScreenNavigationProp
}

const TOTAL_SLIDES = 5

function formatTodayDate(): string {
  const days = ['DOMINGO', 'LUNES', 'MARTES', 'MIÉRCOLES', 'JUEVES', 'VIERNES', 'SÁBADO']
  const months = [
    'ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO',
    'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE',
  ]
  const now = new Date()
  return `${days[now.getDay()]} · ${now.getDate()} ${months[now.getMonth()]}`
}

type SuggestionDia = 'fuerte' | 'moderar' | 'descansar'

interface SuggestionConfig {
  emoji: string
  label: string
  color: string
  bg: string
}

function suggestionConfig(dia: SuggestionDia): SuggestionConfig {
  switch (dia) {
    case 'fuerte':
      return { emoji: '💪', label: 'ENTRENAR FUERTE', color: colors.statusGood, bg: '#0D1A0D' }
    case 'moderar':
      return { emoji: '⚡', label: 'MODERAR HOY', color: colors.statusModerate, bg: '#1A1A0A' }
    case 'descansar':
      return { emoji: '😴', label: 'DESCANSAR', color: colors.statusLow, bg: '#1A0D00' }
  }
}

export default function HomeScreen({ navigation }: Props) {
  const [currentSlide, setCurrentSlide] = useState(0)
  const fadeAnim = useRef(new Animated.Value(1)).current
  const { width, height } = useWindowDimensions()

  const { data: metrics, isLoading: metricsLoading, error: metricsError } = useQuery({
    queryKey: ['metrics', 'today'],
    queryFn: metricsApi.getToday,
  })

  const { data: checkin } = useQuery({
    queryKey: ['checkin', 'today'],
    queryFn: checkinApi.getToday,
  })

  function navigateTo(index: number) {
    if (index < 0) return
    if (index >= TOTAL_SLIDES) {
      navigation.navigate('CheckIn')
      return
    }
    Animated.sequence([
      Animated.timing(fadeAnim, { toValue: 0, duration: 80, useNativeDriver: true }),
      Animated.timing(fadeAnim, { toValue: 1, duration: 150, useNativeDriver: true }),
    ]).start()
    setCurrentSlide(index)
  }

  if (metricsLoading) {
    return (
      <SafeAreaView style={[styles.container, styles.centered]}>
        <ActivityIndicator color={colors.brand} size="large" />
        <Text style={styles.loadingText}>Cargando tu mañana...</Text>
      </SafeAreaView>
    )
  }

  if (metricsError || !metrics) {
    return (
      <SafeAreaView style={[styles.container, styles.centered]}>
        <Text style={styles.errorTitle}>No se pudo conectar al servidor</Text>
        <Text style={styles.errorSubtitle}>Verifica que el backend está corriendo</Text>
      </SafeAreaView>
    )
  }

  const sleepHours = metrics.sleep_seconds
    ? (metrics.sleep_seconds / 3600).toFixed(1)
    : 'Sin datos'
  const hrv = metrics.hrv_last_night_avg
  const hrvStatus = metrics.hrv_status ?? 'Sin datos'
  const readiness = metrics.readiness_score
  const readinessLevel = metrics.readiness_level ?? 'Sin datos'
  const filledBars = readiness ? Math.round(readiness / 10) : 0

  const agentInsight = checkin?.workout_generated ?? null
  const sugerenciaDia: SuggestionDia = (agentInsight?.sugerencia_dia as SuggestionDia) ?? 'moderar'
  const suggestion = suggestionConfig(sugerenciaDia)

  const slides = [
    // Slide 0 — Saludo
    <View key={0} style={[styles.slide, { width, height, backgroundColor: '#0D1117', paddingHorizontal: spacing.xl, paddingTop: spacing.xl }]}>
      <View style={styles.slideTop}>
        <ProgressBars total={TOTAL_SLIDES} current={0} />
        <Text style={[styles.dateLabel, { marginTop: spacing.sm }]}>{formatTodayDate()}</Text>
        <Text style={styles.greeting}>Buenos días,</Text>
        <Text style={styles.userName}>Kenyan 👋</Text>
        <Text style={styles.subGreeting}>Tu reloj estuvo trabajando mientras dormías.</Text>
      </View>
      <Text style={styles.tapHint}>tap para continuar →</Text>
    </View>,

    // Slide 1 — Sueño
    <StorySlide
      key={1}
      backgroundColor='#0A1628'
      accentColor='#60A5FA'
      tag='TU NOCHE'
      bigNumber={sleepHours.toString()}
      bigUnit='horas de sueño'
      coachPhrase='Tu frecuencia respiratoria se mantuvo estable durante la noche.'
      currentSlide={1}
      totalSlides={TOTAL_SLIDES}
    >
      <View style={styles.metricRow}>
        <View style={[styles.metricBox, { backgroundColor: 'rgba(96,165,250,0.1)' }]}>
          <Text style={[styles.metricValue, { color: '#60A5FA' }]}>
            {metrics.avg_respiration ? metrics.avg_respiration.toFixed(1) : '—'}
          </Text>
          <Text style={[styles.metricLabel, { color: '#60A5FA' }]}>resp/min</Text>
        </View>
        <View style={[styles.metricBox, { backgroundColor: 'rgba(96,165,250,0.1)' }]}>
          <Text style={[styles.metricValue, { color: '#60A5FA' }]}>REM</Text>
          <Text style={[styles.metricLabel, { color: '#60A5FA' }]}>fase predominante</Text>
        </View>
      </View>
    </StorySlide>,

    // Slide 2 — HRV
    <StorySlide
      key={2}
      backgroundColor='#0D1F0D'
      accentColor={colors.brand}
      tag='TU SISTEMA NERVIOSO'
      bigNumber={hrv?.toString() ?? 'N/A'}
      bigUnit={`ms de HRV · ${hrvStatus}`}
      coachPhrase='Tu sistema nervioso autónomo refleja cómo estás asimilando el entrenamiento reciente.'
      currentSlide={2}
      totalSlides={TOTAL_SLIDES}
    >
      <View style={styles.comparisonCard}>
        <Text style={[styles.metricLabel, { color: colors.brand }]}>estado HRV</Text>
        <Text style={[styles.comparisonValue, { color: colors.brand }]}>{hrvStatus}</Text>
      </View>
    </StorySlide>,

    // Slide 3 — Readiness
    <StorySlide
      key={3}
      backgroundColor='#1A1A0A'
      accentColor={colors.statusModerate}
      tag='CÓMO AMANECISTE'
      bigNumber={readiness?.toString() ?? 'N/A'}
      bigUnit={`readiness · ${readinessLevel}`}
      coachPhrase='El readiness integra HRV, sueño y estrés acumulado para darte una lectura global de recuperación.'
      currentSlide={3}
      totalSlides={TOTAL_SLIDES}
    >
      <View style={styles.progressBarRow}>
        {Array.from({ length: 10 }, (_, i) => (
          <View
            key={i}
            style={[
              styles.progressBar,
              {
                backgroundColor:
                  i < filledBars ? colors.statusModerate : 'rgba(255,255,255,0.1)',
              },
            ]}
          />
        ))}
      </View>
    </StorySlide>,

    // Slide 4 — Sugerencia dinámica
    <View key={4} style={[styles.slide, { width, height, backgroundColor: suggestion.bg, paddingHorizontal: spacing.xl, paddingTop: spacing.xl }]}>
      <ProgressBars total={TOTAL_SLIDES} current={4} />
      <View style={styles.suggestionContent}>
        <Text style={[styles.slideTag, { color: suggestion.color }]}>QUÉ HACER HOY</Text>
        <Text style={styles.suggestionEmoji}>{suggestion.emoji}</Text>
        <Text style={[styles.suggestionLabel, { color: suggestion.color }]}>{suggestion.label}</Text>
        <Text style={styles.suggestionDetail}>
          {agentInsight?.sugerencia_detalle ?? 'Completa el check-in para recibir tu análisis personalizado.'}
        </Text>
        {agentInsight ? (
          <Text style={styles.checkinDone}>✓ Check-in completado hoy</Text>
        ) : (
          <View style={[styles.ctaCard, { borderColor: `${suggestion.color}33`, backgroundColor: `${suggestion.color}14` }]}>
            <Text style={[styles.ctaHint, { color: suggestion.color }]}>tap para continuar →</Text>
            <Text style={[styles.ctaText, { color: suggestion.color }]}>
              Responde el check-in para personalizar tu día
            </Text>
          </View>
        )}
      </View>
    </View>,
  ]

  return (
    <SafeAreaView style={styles.container}>
      <TouchableWithoutFeedback
        onPress={(e) => {
          const x = e.nativeEvent.locationX
          if (x < width / 2) {
            navigateTo(currentSlide - 1)
          } else {
            navigateTo(currentSlide + 1)
          }
        }}
      >
        <Animated.View style={[styles.animatedContainer, { opacity: fadeAnim }]}>
          {slides[currentSlide]}
        </Animated.View>
      </TouchableWithoutFeedback>
    </SafeAreaView>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bgBase,
  },
  centered: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  loadingText: {
    fontSize: typography.sm,
    color: colors.textMuted,
    marginTop: spacing.md,
  },
  errorTitle: {
    fontSize: typography.base,
    color: colors.textPrimary,
    textAlign: 'center',
  },
  errorSubtitle: {
    fontSize: typography.sm,
    color: colors.textMuted,
    marginTop: spacing.sm,
    textAlign: 'center',
  },
  animatedContainer: {
    flex: 1,
  },
  slide: {
    flex: 1,
    justifyContent: 'space-between',
    paddingBottom: spacing.xl,
  },
  slideTop: {
    flex: 1,
  },
  dateLabel: {
    fontSize: typography.xs,
    color: colors.textMuted,
    letterSpacing: 1.5,
    marginBottom: spacing.xl,
  },
  greeting: {
    fontSize: typography.lg,
    color: colors.textMuted,
  },
  userName: {
    fontSize: 34,
    fontWeight: '700',
    color: colors.textPrimary,
    lineHeight: 40,
    marginBottom: spacing.lg,
  },
  subGreeting: {
    fontSize: typography.base,
    color: colors.textMuted,
    lineHeight: 22,
  },
  tapHint: {
    fontSize: typography.xs,
    color: colors.textMuted,
    opacity: 0.3,
    textAlign: 'right',
    marginBottom: spacing.lg,
  },
  metricRow: {
    flexDirection: 'row',
    gap: spacing.md,
  },
  metricBox: {
    flex: 1,
    borderRadius: radius.md,
    padding: spacing.md,
  },
  metricValue: {
    fontSize: 20,
    fontWeight: '600',
  },
  metricLabel: {
    fontSize: typography.xs,
    opacity: 0.6,
  },
  comparisonCard: {
    backgroundColor: 'rgba(74,222,128,0.08)',
    borderRadius: radius.md,
    padding: spacing.md,
  },
  comparisonValue: {
    fontSize: 20,
    fontWeight: '600',
  },
  progressBarRow: {
    flexDirection: 'row',
    gap: 3,
  },
  progressBar: {
    height: 5,
    flex: 1,
    borderRadius: 2,
  },
  slideTag: {
    fontSize: typography.xs,
    fontWeight: '700',
    letterSpacing: 1.5,
    opacity: 0.7,
    textTransform: 'uppercase',
    marginBottom: spacing.lg,
  },
  suggestionContent: {
    flex: 1,
    justifyContent: 'center',
  },
  suggestionEmoji: {
    fontSize: 48,
    marginBottom: spacing.md,
  },
  suggestionLabel: {
    fontSize: 28,
    fontWeight: '700',
    marginBottom: spacing.md,
  },
  suggestionDetail: {
    fontSize: typography.base,
    color: colors.textSecondary,
    lineHeight: 22,
    fontStyle: 'italic',
    marginBottom: spacing.xl,
  },
  checkinDone: {
    fontSize: typography.xs,
    color: colors.brand,
    opacity: 0.7,
  },
  ctaCard: {
    borderWidth: 0.5,
    borderRadius: radius.md,
    padding: spacing.md,
  },
  ctaHint: {
    fontSize: typography.xs,
    opacity: 0.6,
    marginBottom: 4,
  },
  ctaText: {
    fontSize: typography.sm,
  },
})
