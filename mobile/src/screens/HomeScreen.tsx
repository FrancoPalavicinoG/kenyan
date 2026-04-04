import { StackNavigationProp } from '@react-navigation/stack'
import React, { useRef, useState } from 'react'
import {
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
import { colors, radius, spacing, typography } from '../theme'

type HomeScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Home'>

interface Props {
  navigation: HomeScreenNavigationProp
}

const TOTAL_SLIDES = 5
const USER_NAME = 'Felipe'
const MOCK = {
  sleepHours: 6.6,
  sleepAvg: 7.1,
  respiration: 12,
  hrv: 59,
  hrvHistorical: 42,
  readiness: 61,
  readinessWeekAvg: 33,
  suggestion: 'moderar' as const,
  suggestionDetail:
    'Aprovecha la buena energía pero evita otro HIIT. Dale 24h más a tu sistema nervioso para consolidar esta recuperación.',
}

function formatTodayDate(): string {
  const days = ['DOMINGO', 'LUNES', 'MARTES', 'MIÉRCOLES', 'JUEVES', 'VIERNES', 'SÁBADO']
  const months = [
    'ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO',
    'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE',
  ]
  const now = new Date()
  return `${days[now.getDay()]} · ${now.getDate()} ${months[now.getMonth()]}`
}

export default function HomeScreen({ navigation }: Props) {
  const [currentSlide, setCurrentSlide] = useState(0)
  const fadeAnim = useRef(new Animated.Value(1)).current
  const { width, height } = useWindowDimensions()
  const filledBars = Math.round(MOCK.readiness / 10)

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

  const slides = [
    // Slide 0 — Saludo
    <View key={0} style={[styles.slide, { width, height, backgroundColor: '#0D1117', paddingHorizontal: spacing.xl, paddingTop: spacing.xl }]}>
      <View style={styles.slideTop}>
        <ProgressBars total={TOTAL_SLIDES} current={0} />
        <Text style={[styles.dateLabel, { marginTop: spacing.sm }]}>{formatTodayDate()}</Text>
        <Text style={styles.greeting}>Buenos días,</Text>
        <Text style={styles.userName}>{USER_NAME} 👋</Text>
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
      bigNumber={MOCK.sleepHours.toFixed(1)}
      bigUnit='horas de sueño'
      coachPhrase={`Ligeramente bajo tu promedio de ${MOCK.sleepAvg}h — pero la calidad fue buena. Tu frecuencia respiratoria se mantuvo estable.`}
      currentSlide={1}
      totalSlides={TOTAL_SLIDES}
    >
      <View style={styles.metricRow}>
        <View style={[styles.metricBox, { backgroundColor: 'rgba(96,165,250,0.1)' }]}>
          <Text style={[styles.metricValue, { color: '#60A5FA' }]}>{MOCK.respiration}</Text>
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
      bigNumber={MOCK.hrv.toString()}
      bigUnit={`ms de HRV · BALANCED`}
      coachPhrase={`${MOCK.hrv - MOCK.hrvHistorical}ms por encima de tu histórico de ${MOCK.hrvHistorical}ms. Tu cuerpo está respondiendo bien a la carga reciente.`}
      currentSlide={2}
      totalSlides={TOTAL_SLIDES}
    >
      <View style={styles.comparisonCard}>
        <Text style={[styles.metricLabel, { color: colors.brand }]}>promedio 30 días</Text>
        <Text style={[styles.comparisonValue, { color: colors.brand }]}>{MOCK.hrvHistorical} ms</Text>
      </View>
    </StorySlide>,

    // Slide 3 — Readiness
    <StorySlide
      key={3}
      backgroundColor='#1A1A0A'
      accentColor={colors.statusModerate}
      tag='CÓMO AMANECISTE'
      bigNumber={MOCK.readiness.toString()}
      bigUnit='readiness · MODERATE'
      coachPhrase={`Rebote claro desde el promedio de ${MOCK.readinessWeekAvg} de esta semana. Tu cuerpo salió del hoyo de fatiga — pero aún no al tope.`}
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

    // Slide 4 — Sugerencia
    <View key={4} style={[styles.slide, { width, height, backgroundColor: '#1A0D00', paddingHorizontal: spacing.xl, paddingTop: spacing.xl }]}>
      <ProgressBars total={TOTAL_SLIDES} current={4} />
      <View style={styles.suggestionContent}>
        <Text style={[styles.slideTag, { color: colors.statusLow }]}>QUÉ HACER HOY</Text>
        <Text style={styles.suggestionEmoji}>⚡</Text>
        <Text style={[styles.suggestionLabel, { color: colors.statusLow }]}>MODERAR HOY</Text>
        <Text style={styles.suggestionDetail}>{MOCK.suggestionDetail}</Text>
        <View style={styles.ctaCard}>
          <Text style={styles.ctaHint}>tap para continuar →</Text>
          <Text style={styles.ctaText}>Responde el check-in para personalizar tu día</Text>
        </View>
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
  ctaCard: {
    backgroundColor: 'rgba(251,146,60,0.08)',
    borderWidth: 0.5,
    borderColor: 'rgba(251,146,60,0.2)',
    borderRadius: radius.md,
    padding: spacing.md,
  },
  ctaHint: {
    fontSize: typography.xs,
    color: colors.statusLow,
    opacity: 0.6,
    marginBottom: 4,
  },
  ctaText: {
    fontSize: typography.sm,
    color: colors.statusLow,
  },
})
