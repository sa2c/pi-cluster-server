import React from 'react';
import ReactDOM from 'react-dom';

function Avatar(props) {
    if (typeof props.whom == 'undefined') {
        return null;
    } else {
        return (
            <img className="avatar-small" src={ "/static/avatars/"+ props.whom + ".png" } />
        );
    }
}

export { Avatar };
