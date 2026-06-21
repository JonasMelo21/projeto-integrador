import { createBrowserRouter } from "react-router";
import { RootLayout } from "./components/RootLayout";
import { LoginPage } from "./components/LoginPage";
import { HomePage } from "./components/HomePage";
import { PropertyDetailsPage } from "./components/PropertyDetailsPage";
import { ChatAIPage } from "./components/ChatAIPage";
import { MapPage } from "./components/MapPage";
import { FavoritesPage } from "./components/FavoritesPage";
import { ProfilePage } from "./components/ProfilePage";

export const router = createBrowserRouter([
  {
    path: "/login",
    Component: LoginPage,
  },
  {
    path: "/",
    Component: RootLayout,
    children: [
      { index: true, Component: HomePage },
      { path: "property/:id", Component: PropertyDetailsPage },
      { path: "chat", Component: ChatAIPage },
      { path: "map", Component: MapPage },
      { path: "favorites", Component: FavoritesPage },
      { path: "profile", Component: ProfilePage },
    ],
  },
]);
