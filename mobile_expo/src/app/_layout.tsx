import { Stack } from 'expo-router';

export default function RootLayout() {
  return (
    <Stack
      screenOptions={{
        headerShown: false,
        animationEnabled: true,
      }}
    >
      <Stack.Screen name="index" options={{ animationEnabled: false }} />
      <Stack.Screen name="(tabs)" options={{ animationEnabled: false }} />
    </Stack>
  );
}
