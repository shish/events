import React from "react";
import css from "./Tip.module.scss";
import { Tooltip } from "react-tooltip";

export function TagList({ tags }: { tags: string[] }): React.ReactElement {
    return (
        <>
            {tags.map((tag, index) => (
                <React.Fragment key={tag}>
                    <Tag name={tag} />
                    {index !== tags.length - 1 && ", "}
                </React.Fragment>
            ))}
        </>
    );
}

export function Tag({ name }: { name: string }): React.ReactElement {
    const id = name.replace(/[^a-zA-Z0-9]/g, "_");
    return (
        <>
            #{name}
        </>
    );
}
