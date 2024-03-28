/* eslint-disable */
import * as types from './graphql';
import { TypedDocumentNode as DocumentNode } from '@graphql-typed-document-node/core';

/**
 * Map of all GraphQL operations in the project.
 *
 * This map has several performance disadvantages:
 * 1. It is not tree-shakeable, so it will include all operations in the project.
 * 2. It is not minifiable, so the string of a GraphQL query will be multiple times inside the bundle.
 * 3. It does not support dead code elimination, so it will add unused operations.
 *
 * Therefore it is highly recommended to use the babel or swc plugin for production.
 */
const documents = {
    "\n    mutation updateUser(\n        $password: String!\n        $username: String!\n        $password1: String!\n        $password2: String!\n        $email: String!\n    ) {\n        updateUser(\n            password: $password\n            username: $username\n            password1: $password1\n            password2: $password2\n            email: $email\n        ) {\n            ...UserLogin\n        }\n    }\n": types.UpdateUserDocument,
    "\n    query getEvents {\n        events {\n            ...EventView\n        }\n    }\n": types.GetEventsDocument,
    "\n    fragment EventView on Event {\n        id\n        title\n        description\n        tags\n        owner {\n            username\n        }\n    }\n": types.EventViewFragmentDoc,
    "\n    query getEvent($eventId: Int!) {\n        event(eventId: $eventId) {\n            ...EventView\n        }\n    }\n": types.GetEventDocument,
    "\n    query getFriends {\n        me: user {\n            friends {\n                username\n            }\n            friendsOutgoing {\n                username\n            }\n            friendsIncoming {\n                username\n            }\n        }\n    }\n": types.GetFriendsDocument,
    "\n    mutation addFriend($username: String!) {\n        addFriend(username: $username)\n    }\n": types.AddFriendDocument,
    "\n    mutation removeFriend($username: String!) {\n        removeFriend(username: $username)\n    }\n": types.RemoveFriendDocument,
    "\n    fragment UserLogin on User {\n        username\n        email\n    }\n": types.UserLoginFragmentDoc,
    "\n    query getMe {\n        me: user {\n            ...UserLogin\n        }\n    }\n": types.GetMeDocument,
    "\n    mutation createUser(\n        $username: String!\n        $password1: String!\n        $password2: String!\n        $email: String!\n    ) {\n        createUser(\n            username: $username\n            password1: $password1\n            password2: $password2\n            email: $email\n        ) {\n            ...UserLogin\n        }\n    }\n": types.CreateUserDocument,
    "\n    mutation login($username: String!, $password: String!) {\n        login(username: $username, password: $password) {\n            ...UserLogin\n        }\n    }\n": types.LoginDocument,
    "\n    mutation logout {\n        logout\n    }\n": types.LogoutDocument,
};

/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 *
 *
 * @example
 * ```ts
 * const query = graphql(`query GetUser($id: ID!) { user(id: $id) { name } }`);
 * ```
 *
 * The query argument is unknown!
 * Please regenerate the types.
 */
export function graphql(source: string): unknown;

/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n    mutation updateUser(\n        $password: String!\n        $username: String!\n        $password1: String!\n        $password2: String!\n        $email: String!\n    ) {\n        updateUser(\n            password: $password\n            username: $username\n            password1: $password1\n            password2: $password2\n            email: $email\n        ) {\n            ...UserLogin\n        }\n    }\n"): (typeof documents)["\n    mutation updateUser(\n        $password: String!\n        $username: String!\n        $password1: String!\n        $password2: String!\n        $email: String!\n    ) {\n        updateUser(\n            password: $password\n            username: $username\n            password1: $password1\n            password2: $password2\n            email: $email\n        ) {\n            ...UserLogin\n        }\n    }\n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n    query getEvents {\n        events {\n            ...EventView\n        }\n    }\n"): (typeof documents)["\n    query getEvents {\n        events {\n            ...EventView\n        }\n    }\n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n    fragment EventView on Event {\n        id\n        title\n        description\n        tags\n        owner {\n            username\n        }\n    }\n"): (typeof documents)["\n    fragment EventView on Event {\n        id\n        title\n        description\n        tags\n        owner {\n            username\n        }\n    }\n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n    query getEvent($eventId: Int!) {\n        event(eventId: $eventId) {\n            ...EventView\n        }\n    }\n"): (typeof documents)["\n    query getEvent($eventId: Int!) {\n        event(eventId: $eventId) {\n            ...EventView\n        }\n    }\n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n    query getFriends {\n        me: user {\n            friends {\n                username\n            }\n            friendsOutgoing {\n                username\n            }\n            friendsIncoming {\n                username\n            }\n        }\n    }\n"): (typeof documents)["\n    query getFriends {\n        me: user {\n            friends {\n                username\n            }\n            friendsOutgoing {\n                username\n            }\n            friendsIncoming {\n                username\n            }\n        }\n    }\n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n    mutation addFriend($username: String!) {\n        addFriend(username: $username)\n    }\n"): (typeof documents)["\n    mutation addFriend($username: String!) {\n        addFriend(username: $username)\n    }\n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n    mutation removeFriend($username: String!) {\n        removeFriend(username: $username)\n    }\n"): (typeof documents)["\n    mutation removeFriend($username: String!) {\n        removeFriend(username: $username)\n    }\n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n    fragment UserLogin on User {\n        username\n        email\n    }\n"): (typeof documents)["\n    fragment UserLogin on User {\n        username\n        email\n    }\n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n    query getMe {\n        me: user {\n            ...UserLogin\n        }\n    }\n"): (typeof documents)["\n    query getMe {\n        me: user {\n            ...UserLogin\n        }\n    }\n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n    mutation createUser(\n        $username: String!\n        $password1: String!\n        $password2: String!\n        $email: String!\n    ) {\n        createUser(\n            username: $username\n            password1: $password1\n            password2: $password2\n            email: $email\n        ) {\n            ...UserLogin\n        }\n    }\n"): (typeof documents)["\n    mutation createUser(\n        $username: String!\n        $password1: String!\n        $password2: String!\n        $email: String!\n    ) {\n        createUser(\n            username: $username\n            password1: $password1\n            password2: $password2\n            email: $email\n        ) {\n            ...UserLogin\n        }\n    }\n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n    mutation login($username: String!, $password: String!) {\n        login(username: $username, password: $password) {\n            ...UserLogin\n        }\n    }\n"): (typeof documents)["\n    mutation login($username: String!, $password: String!) {\n        login(username: $username, password: $password) {\n            ...UserLogin\n        }\n    }\n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n    mutation logout {\n        logout\n    }\n"): (typeof documents)["\n    mutation logout {\n        logout\n    }\n"];

export function graphql(source: string) {
  return (documents as any)[source] ?? {};
}

export type DocumentType<TDocumentNode extends DocumentNode<any, any>> = TDocumentNode extends DocumentNode<  infer TType,  any>  ? TType  : never;