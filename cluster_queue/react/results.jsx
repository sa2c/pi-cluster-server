import React from 'react';
import ReactDOM from 'react-dom';

import {
  SimulationList
} from './simulationlist.jsx'

import css from '../assets/styles/leaderboard.sass'

function MainPanel(props) {
  const img_src = "simulations/" + props.currentSimulation +
    "/elmeroutput0001-velomagn.png"

  return (
      <div className="simulation-viewer">
        <img id="result-main-image"
           src={img_src}
           alt="Simulation Main View"
           width="100%" />
      </div>
  );
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
          state[target] = result;

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

  simulationChoiceHandler(sim_id) {
    this.setState({
      currentSimulation: sim_id
    });
  }

  render() {
      const dragValues = new Set(this.state.bestSimulations.concat(this.state.recentSimulations).map((sim) => sim.drag))
      const maxDrag = Math.max(...dragValues)

      const best = this.state.bestSimulations.map((sim) => {
          const update = {'fractional-drag' : sim['drag']/maxDrag }
          return { ...sim, ...update}
      });

      const recent = this.state.recentSimulations.map((sim) => {
          const update = {'fractional-drag' : sim['drag']/maxDrag }
          return { ...sim, ...update}
      });

    return (
      <div className="root">
                  <SimulationList title="Fastest"
                                  showIndex={ true }
                                  percentageKey='fractional-drag'
                                  simulations={ best }
                                  currentSimulation={this.state.currentSimulation}
                                  onClick={ this.simulationChoiceHandler.bind(this) }/>
                  <MainPanel currentSimulation={this.state.currentSimulation}/>
                  <SimulationList title="Latest"
                                  showIndex={ false }
                                  percentageKey='fractional-drag'
                                  simulations={ recent }
                                  currentSimulation={this.state.currentSimulation}
                                  onClick={ this.simulationChoiceHandler.bind(this) }/>
                </div>
    );
  }
}

ReactDOM.render(
  <Layout />,
  document.getElementById('root-results')
);
