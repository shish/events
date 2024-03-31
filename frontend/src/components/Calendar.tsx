import { Link } from "react-router-dom";
import { EventViewFragment } from "../gql/graphql";
import css from "../pages/EventList.module.scss";
import { sectionMaker } from "./Section";
import { Tag, TagList } from "./Tag";


export const Calendar = sectionMaker(function({events}: {events: EventViewFragment[]}) {
    return (
        <>
            <h3>Calendar (<a href={`/calendar/global.ics`}>.ics file</a>)</h3>
            <p>TODO: make this look more like a calendar</p>
            <ul>
                {events.map(event => (
                    <li key={event.id}>
                        <Link to={`/event/${event.id}`}>{event.title}</Link>{" - "}
                        <TagList tags={event.tags}/>
                    </li>
                ))}
            </ul>
        </>
    );
}, css.lists);