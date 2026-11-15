import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: '#60a5fa',
        tabBarInactiveTintColor: '#94a3b8',
        tabBarStyle: {
          height: 75,
          paddingBottom: 15,
          backgroundColor: '#1A1A1A',
        },
      }}
    >
      <Tabs.Screen
        name="home"
        options={{
          title: 'Home',
          tabBarIcon: ({ focused }) => (
            <Ionicons name="home-outline" color={focused ? '#60a5fa' : '#94a3b8'} size={22} />
          ),
        }}
      />
      <Tabs.Screen
        name="explore"
        options={{
          title: 'Explore',
          tabBarIcon: ({ focused }) => (
            <Ionicons
              name="compass-outline"
              color={focused ? '#60a5fa' : '#94a3b8'}
              size={22}
            />
          ),
        }}
      />
    </Tabs>
  );
}
