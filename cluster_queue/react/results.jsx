import React from 'react';
import ReactDOM from 'react-dom';

import { SimulationList } from './simulationlist.jsx'

import css from '../assets/styles/leaderboard.sass'

function MainPanel(props) {
  const img_src = "simulations/" + props.currentSimulation +
    "/elmeroutput0001-velomagn.png"

  return (
    <img id="result-main-image"
         src={img_src}
         alt="Simulation Main View"
         width="100%" />
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
    return (
      <div className="container">
              <div className="columns">
                <div className="column is-two-thirds is-vertical-centre">
                  <MainPanel currentSimulation={this.state.currentSimulation}/>
                </div>
                <div id="leaderboard" className="column is-scroll">
                  <SimulationList title="Leaderboard"
                                  showIndex={ true }
                                  simulations={ this.state.bestSimulations }
                                  currentSimulation={this.state.currentSimulation}
                                  onClick={ this.simulationChoiceHandler.bind(this) }/>
                </div>
                <div id="recent-simulations" className="column is-scroll">
                  <SimulationList title="Recent"
                                  showIndex={ false }
                                  simulations={ this.state.recentSimulations }
                                  currentSimulation={this.state.currentSimulation}
                                  onClick={ this.simulationChoiceHandler.bind(this) }/>
                </div>
              </div>
            </div>
    );
  }
}

ReactDOM.render(
  <Layout />,
  document.getElementById('root-results')
);
