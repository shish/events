import { Page } from "../components/Page";
import { useContext } from "react";
import { UserContext } from "../providers/LoginProvider";
import { LogIn } from "../components/Login";
import { UserInfo } from "../components/UserInfo";
import css from "./EventList.module.scss";
import { Calendar } from "../components/Calendar";
import { About } from "../components/About";
import { useQuery } from "@apollo/client";
import { LoadingPage } from "../components/LoadingPage";
import { ErrorPage } from "../components/ErrorPage";
import { graphql, useFragment as fragCast } from "../gql";
import { EVENT_VIEW_FRAGMENT } from "./EventView";

export const GET_EVENTS = graphql(`
    query getEvents {
        events {
            ...EventView
        }
    }
`);

export function EventList() {
    const { me } = useContext(UserContext);
    const q = useQuery(GET_EVENTS);

    if (q.loading) {
        return <LoadingPage />;
    }
    if (q.error) {
        return <ErrorPage error={q.error} />;
    }
    const events = q.data!.events.map(x => fragCast(EVENT_VIEW_FRAGMENT, x));

    return (
        <Page className={css.page}>
            {me ? <UserInfo /> : <LogIn />}
            <Calendar events={events} />
            <About />
        </Page>
    );
}
