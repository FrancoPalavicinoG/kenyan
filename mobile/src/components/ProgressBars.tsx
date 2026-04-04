import React from 'react'
import { StyleSheet, View } from 'react-native'

interface ProgressBarsProps {
  total: number
  current: number
}

export default function ProgressBars({ total, current }: ProgressBarsProps) {
  return (
    <View style={styles.container}>
      {Array.from({ length: total }, (_, i) => (
        <View
          key={i}
          style={[
            styles.bar,
            {
              backgroundColor:
                i <= current
                  ? 'rgba(255,255,255,0.9)'
                  : 'rgba(255,255,255,0.25)',
            },
          ]}
        />
      ))}
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    gap: 3,
    marginBottom: 12,
  },
  bar: {
    flex: 1,
    height: 2,
    borderRadius: 1,
  },
})
