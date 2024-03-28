import React, { useContext } from "react";
import { useQuery } from "@apollo/client";
import { graphql, useFragment as fragCast } from "../gql";
import { Navigate, useParams } from "react-router-dom";
import { ErrorPage } from "../components/ErrorPage";
import { LoadingPage } from "../components/LoadingPage";
import css from "./EventView.module.scss";
import { Page } from "../components/Page";
import { UserContext } from "../providers/LoginProvider";

export const EVENT_VIEW_FRAGMENT = graphql(`
    fragment EventView on Event {
        id
        title
        description
        tags
        owner {
            username
        }
    }
`);

export const GET_EVENT = graphql(`
    query getEvent($eventId: Int!) {
        event(eventId: $eventId) {
            ...EventView
        }
    }
`);

export function EventView() {
    ///////////////////////////////////////////////////////////////////
    // Hooks
    const { event_id } = useParams();
    const { me } = useContext(UserContext);
    const q = useQuery(GET_EVENT, {
        variables: { eventId: parseInt(event_id!, 10) },
    });
    if (!me) {
        return <Navigate to="/" />;
    }

    ///////////////////////////////////////////////////////////////////
    // Hook edge case handling
    if (q.loading) {
        return <LoadingPage />;
    }
    if (q.error) {
        return <ErrorPage error={q.error} />;
    }
    const event = fragCast(EVENT_VIEW_FRAGMENT, q.data?.event);
    if (!event) {
        return (
            <ErrorPage
                error={{ message: `No event with the ID ${event_id}` }}
            />
        );
    }

    ///////////////////////////////////////////////////////////////////
    // Render

    return (
        <Page title={event.title} className={css.page}>
            <section style={{gridArea: "description"}}>
                <h3>{event.title}</h3>
                <p>{event.description}</p>
                <p>Created by {event.owner.username}</p>
            </section>
        </Page>
    );
}
