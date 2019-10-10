import React from 'react';
import ReactDOM from 'react-dom';

import {
  colourJob
} from './receivesimulations.jsx'

import {
  SimulationList
} from './simulationlist.jsx'

import css from '../assets/styles/leaderboard.sass'

function SimulationViewer(props) {
    console.log(typeof props.currentSimulation)
  if (typeof props.currentSimulation == 'undefined') {
    return null;
  } else if (typeof props.currentSimulation == 'number') {
      // simulation is initially set to a number as a placeholder
      // quite an ugly hack, but it avoid undefined values everywhere
      return (
          <div className="simulation-viewer">
              <div className="placeholder">
                  Please select a simulation to view
              </div>
          </div>
      );
  } else {
    const sim = props.currentSimulation

    const img_rgb = "simulations/" + sim.id + "/rgb_with_contour.png"
    const img_depth = "simulations/" + sim.id + "/depth.png"

    const colour = sim.colour

    return (
      <div className="simulation-viewer"
        style={{color: colour}}>
        <img id="result-rgb-image" src={img_rgb} alt="RGB image" />
        <img id="result-depth-image" src={img_depth} alt="RGB image" />
          </div>
    );
  }
}

class Layout extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      bestSimulations: [],
      recentSimulations: [],
      currentSimulation: 1,
      errors: []
    };
  }

  // fetch best simulations from server and update in component state
  simulationFetcher(url, target) {
    fetch(url)
      .then(res => res.json())
      .then(
        (result) => {
          var state = {};
          const jobs = result.map((job) => colourJob(job))
          state[target] = jobs;

          this.setState(state);
        },
        (error) => {
          this.setState({
            errors: ["failed to load max drag data"]
          });
        }
      );
  }

  fetchBestSimulations() {
    this.simulationFetcher("/simulations/max_drag/10", 'bestSimulations');
  }

  fetchRecentSimulations() {
    this.simulationFetcher("/simulations/recent/10", 'recentSimulations');
  }
  componentDidMount() {
    this.fetchBestSimulations();
    this.fetchRecentSimulations();
  }

  simulationChoiceHandler(sim) {
    this.setState({
      currentSimulation: sim
    });
  }

  render() {
    const dragValues = new Set(this.state.bestSimulations.concat(this.state
        .recentSimulations)
      .map((sim) => sim.drag))
    const maxDrag = Math.max(...dragValues)

    const best = this.state.bestSimulations.map((sim) => {
      const update = {
        'fractional-drag': sim['drag'] / maxDrag
      }
      return {
        ...sim,
        ...update
      }
    });

    const recent = this.state.recentSimulations.map((sim) => {
      const update = {
        'fractional-drag': sim['drag'] / maxDrag
      }
      return {
        ...sim,
        ...update
      }
    });

    return (
      <div className="root">
                  <SimulationList title="Fastest"
                                  showIndex={ true }
                                  percentageKey='fractional-drag'
                                  simulations={ best }
                                  currentSimulation={this.state.currentSimulation}
                                  clickHandler={ this.simulationChoiceHandler.bind(this) }/>
                  <SimulationViewer currentSimulation={this.state.currentSimulation}/>
                  <SimulationList title="Latest"
                                  showIndex={ false }
                                  percentageKey='fractional-drag'
                                  simulations={ recent }
                                  currentSimulation={this.state.currentSimulation}
                                  clickHandler={ this.simulationChoiceHandler.bind(this) }/>
                </div>
    );
  }
}

ReactDOM.render(
  <Layout />,
  document.getElementById('root-results')
);
