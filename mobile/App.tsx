import { NavigationContainer } from '@react-navigation/native'
import { createStackNavigator } from '@react-navigation/stack'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import React from 'react'
import { GestureHandlerRootView } from 'react-native-gesture-handler'
import CheckInScreen from './src/screens/CheckInScreen'
import HomeScreen from './src/screens/HomeScreen'
import InsightScreen from './src/screens/InsightScreen'
import { colors } from './src/theme'

export type RootStackParamList = {
  Home: undefined
  CheckIn: undefined
  Insight: { checkinId: number }
}

const Stack = createStackNavigator<RootStackParamList>()
const queryClient = new QueryClient()

export default function App() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <QueryClientProvider client={queryClient}>
        <NavigationContainer>
          <Stack.Navigator
            initialRouteName="Home"
            screenOptions={{
              headerShown: false,
              cardStyle: { backgroundColor: colors.bgBase },
            }}
          >
            <Stack.Screen name="Home" component={HomeScreen} />
            <Stack.Screen name="CheckIn" component={CheckInScreen} />
            <Stack.Screen name="Insight" component={InsightScreen} />
          </Stack.Navigator>
        </NavigationContainer>
      </QueryClientProvider>
    </GestureHandlerRootView>
  )
}
