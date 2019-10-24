import React from 'react';
import ReactDOM from 'react-dom';

import {
  Avatar
} from './avatar.jsx'

import css from '../assets/styles/simulation-list.sass'

function SimulationList(props) {
  const simulations = props.simulations.map((sim, index) => {

    // set isCurrent
    var isCurrent = false
    if (typeof props.currentSimulation !== 'undefined') {
      isCurrent = sim.id == props.currentSimulation.id
    }

    return <SimulationView key={sim['id']}
                               simulation={sim}
                               showIndex={props.showIndex}
                               index={index + 1}
                               percentageKey={props.percentageKey}
                               isCurrent={isCurrent}
                               clickHandler={props.clickHandler}/>;

  });

  return (
    <div className="simulation-pane pane">
            <h1 className="title has-text-centered">{ props.title }</h1>
      <div className="scrolling">
            {simulations}
      </div>
        </div>
  )

}

function SimulationView(props) {

  const simulation = props.simulation;

  if (simulation == undefined) {
    return null;
  } else {
    const sim_id = simulation['id'];

    var rgb_url = "static/sim-image-loading.gif";
    var depth_url = "static/sim-image-loading.gif";
    var image_class = ""

    if (simulation['images-available']) {
      rgb_url = "simulations/" + sim_id +
        "/rgb_with_contour.png";
      depth_url = "simulations/" + sim_id +
        "/depth.png";
    } else {
      image_class = " loading";
    }
    var progressBar = null;

    if (props.percentageKey in simulation) {
      progressBar = (
        <div className="progress-indicator-container">
                    <div className="progress-indicator" style={{width : simulation.progress + "%"}}/>
        </div>);
    }

    // (slightly hacky) setting of simulation name if not provided
    var simulation_name;
    if (simulation['name']) {
      simulation_name = simulation['name'];
    } else {
      simulation_name = 'Simulation';
    }
    simulation_name = simulation_name + " (" + simulation.id + ")";

    // Add index to title if showIndex is true
    if (props.showIndex) {
      simulation_name = '#' + props.index + ' ' + simulation_name;
    }

    const outlineColour = props.isCurrent ? simulation['colour'] : "";

    return (
      <div className={"simulation-view" + (props.isCurrent ? " selected" : "")}
            onClick={() => props.clickHandler(simulation)}
            style={{ "color" : outlineColour}} >
        <div className="simulation-heading">
                    <Avatar whom={simulation.avatar_id} />
                    <div className="right">
                        <div className="sim-title"> {simulation_name} </div>
                        {progressBar}
                    </div>
                </div>
                <div className="simulation-data">
                    <img className={"simulation-capture left" + image_class} src={rgb_url} />
                    <img className={"simulation-capture right" + image_class} src={depth_url} />
                </div>
            </div>
    );
  }
}

export {
  SimulationList
};
