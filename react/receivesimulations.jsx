import React from 'react';
import ReactDOM from 'react-dom';

const defaultAvatarColour = "#e3e3e3"

const avatarColours = [
    "#f26a44",
    "#3f3d31",
    "#d3ce3e",
    "#2eaeb7",
    "#fedb7d",
    "#2eaeb7",
    "#fedb7d",
    "#3f3d31",
    "#d3ce3e",
    "#2eaeb7",
    "#fedb7d",
    "#2eaeb7",
    "#f26a44",
    "#2eaeb7",
    "#fffce9",
    "#f26a44",
    "#d3ce3e",
    "#3f3d31",
    "#d3ce3e",
    "#d3ce3e",
    "#fedb7d",
    "#3f3d31",
    "#fedb7d",
    "#2eaeb7",
    "#d3ce3e",
]


function colourJob(job) {
    if(typeof job == 'undefined') {
        job = {}
    }

    return {
        ...job,
        ...{ colour: avatarColours[job.avatar - 1] }
    }
}

// set the default job attributes
//colour: defaultAvatarColour


// set the (avatar) colour for this job


export { colourJob }
