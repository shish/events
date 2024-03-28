import css from "../pages/EventList.module.scss";
import { sectionMaker } from "./Section";


export const About = sectionMaker(function() {
    return (
        <>
            <h3>About</h3>
            <p>An Index for Events</p>
        </>
    );
}, css.about);