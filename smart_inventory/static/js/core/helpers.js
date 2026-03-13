import {isAnonymousUser} from "../core/helpers.js";

if (isAnonymousUser()) {
    console.log("User is not logged in");
}
