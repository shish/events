import {
    createBrowserRouter,
    createRoutesFromElements,
    Route,
} from "react-router-dom";

import { ErrorPage } from "../components/ErrorPage";
import { EventList } from "./EventList";
import { EventView } from "./EventView";
import { Friends } from "./Friends";
import { User } from "./User";

export const router = createBrowserRouter(
    createRoutesFromElements(
        <Route path="/" errorElement={<ErrorPage />}>
            <Route index element={<EventList />} />
            <Route path="event/:event_id" element={<EventView />} />
            <Route path="friends" element={<Friends />} />
            <Route path="user" element={<User />} />
        </Route>,
    ),
);
