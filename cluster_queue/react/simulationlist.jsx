import React from 'react';
import ReactDOM from 'react-dom';

import { Avatar } from './avatar.jsx'

import css from '../assets/styles/simulation-list.sass'

function SimulationList(props) {
    const simulations = props.simulations.map((sim, index) => {
        var isCurrent = index == props.currentIndex

        return <SimulationView key={sim['id']} simulation={sim} showIndex={props.showIndex} index={index + 1} percentageKey={props.percentageKey} current={isCurrent}/>;

    });
    return (
        <div className="simulation-pane pane">
            <h1 className="title has-text-centered">{ props.title }</h1>
            {simulations}
        </div>
    )

}

function SimulationView(props) {

    const simulation = props.simulation;

    if (simulation == undefined) {
        return null;
    } else {
        const sim_id = simulation['id'];

        const rgb_url = "simulations/" + sim_id +
                          "/rgb_with_contour.png";
        const depth_url = "simulations/" + sim_id +
                        "/depth.png";

        var progressBar = null;

        if (props.percentageKey in simulation) {
            progressBar =
                <div className="progress-indicator-container">
                    <div className="progress-indicator" style={{width : simulation.progress + "%"}}/>
                </div>
        }

        // (slightly hacky) setting of simulation name if not provided
        var simulation_name
        if(simulation['name']) {
            simulation_name = simulation['name']
        } else {
            simulation_name = 'Simulation'
        }

        // Add index to title if showIndex is true
        if(props.showIndex) {
            simulation_name = '#' + props.index + ' ' + simulation_name
        }

        return (
            <div className={"simulation-view" + (props.isCurrent ? " selected" : "")}>
                <div className="simulation-heading">
                    <Avatar whom={simulation.avatar} />
                    <div className="right">
                        <div className="sim-title"> {simulation_name} </div>
                        {progressBar}
                    </div>
                </div>
                <div className="simulation-data">
                    <img className="simulation-capture left" src={rgb_url} />
                    <img className="simulation-capture right" src={depth_url} />
                </div>
            </div>
        );
    }
}

export { SimulationList };
