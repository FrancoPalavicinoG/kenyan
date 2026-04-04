import React from 'react'
import { StyleSheet, Text, View, useWindowDimensions } from 'react-native'
import { colors, spacing, typography } from '../theme'
import ProgressBars from './ProgressBars'

interface StorySlideProps {
  backgroundColor: string
  accentColor: string
  tag: string
  bigNumber?: string
  bigUnit?: string
  coachPhrase: string
  children?: React.ReactNode
  currentSlide: number
  totalSlides: number
}

export default function StorySlide({
  backgroundColor,
  accentColor,
  tag,
  bigNumber,
  bigUnit,
  coachPhrase,
  children,
  currentSlide,
  totalSlides,
}: StorySlideProps) {
  const { width, height } = useWindowDimensions()

  return (
    <View style={[styles.container, { width, height, backgroundColor, paddingHorizontal: spacing.xl, paddingTop: spacing.xl }]}>
      <ProgressBars total={totalSlides} current={currentSlide} />

      <Text style={[styles.tag, { color: accentColor }]}>{tag}</Text>

      {bigNumber && (
        <Text style={[styles.bigNumber, { color: accentColor }]}>{bigNumber}</Text>
      )}
      {bigUnit && (
        <Text style={[styles.bigUnit, { color: accentColor }]}>{bigUnit}</Text>
      )}

      <Text style={styles.coachPhrase}>{coachPhrase}</Text>

      {children && <View style={styles.children}>{children}</View>}
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  tag: {
    fontSize: typography.xs,
    fontWeight: '700',
    letterSpacing: 1.5,
    opacity: 0.7,
    textTransform: 'uppercase',
    marginBottom: spacing.sm,
    marginTop: spacing.sm,
  },
  bigNumber: {
    fontSize: 72,
    fontWeight: '700',
    letterSpacing: -2,
    lineHeight: 76,
  },
  bigUnit: {
    fontSize: typography.sm,
    opacity: 0.7,
    marginBottom: spacing.lg,
  },
  coachPhrase: {
    fontSize: typography.base,
    color: colors.textSecondary,
    lineHeight: 22,
    fontStyle: 'italic',
  },
  children: {
    marginTop: spacing.lg,
  },
})
