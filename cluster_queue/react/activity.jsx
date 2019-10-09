import React from 'react';
import ReactDOM from 'react-dom';

import ClusterSchematic from './clusterschematic.jsx'

import css from '../assets/styles/activity.sass'

class Layout extends React.Component {
  constructor(props) {
    super(props);

    const cores = 12;

    this.state = {
      nCores: cores,
      cpuActivity: Array(cores)
        .fill(0),
      cpuActivityHistory: Array(cores)
        .fill(0)
        .map((v) => {
          return [v];
        }),
      maxNumHistoryEntries: 20,
      dataUrl: props.dataUrl,
      serverUpdateInterval: 5000,
      pending: [],
      running: [],
    };

  }

  componentDidMount() {
    this.fetchActivity();
    setInterval(this.fetchActivity.bind(this), this.state
      .serverUpdateInterval);
  }

  // fetch best simulations from server and update in component state
  fetchActivity() {
    fetch(this.state.dataUrl)
      .then(res => res.json())
      .then(
        (result) => {
          const cpuHistory =
            this.state.cpuActivityHistory.map((series, index) => {
              const next_val = result['cpu_usage'][index];
              const nmax = this.state.maxNumHistoryEntries;
              return series.concat(next_val)
                .slice(series.length - nmax + 1, series.length + 1);
            });

          this.setState({
            cpuActivity: result['cpu_usage'],
            cpuActivityHistory: cpuHistory,
            pending: result['pending'],
            running: result['running'],

          });
        },
        (error) => {
          console.log("failed to load data from " + this.state.dataUrl);
        }
      );
  }

  render() {
    return (
      <div id="layout">
        <div className="lhs-pane">
          <ClusterSchematic cpuActivity={this.state.cpuActivity} running={this.state.running} />
        </div>
        <div className="rhs-pane">
          <h1 className="title is-2">Waiting</h1>
          <SimulationList simulations={this.state.pending}/>
          <h1 className="title is-2">Running</h1>
          <SimulationList simulations={this.state.running}/>
        </div>
      </div>
    );
  }
}

function SimulationList(props) {
  return props.simulations.map((sim) => {
    return <SimulationView key={sim['id']} simulation={sim}/>;
  });
}

function SimulationView(props) {

  const simulation = props.simulation;

  if (simulation == undefined) {
    return <div className="simulation-data"/>;
  } else {
    const sim_id = simulation['id'];

    const image_url = "simulations/" + sim_id +
      "/elmeroutput0001-velomagn.png";

    const image_alt = "Simulation " + sim_id + " image";

    return (
      <div className="simulation-data" style={{width: "30%", float : "left" }}>
            <p>
              {simulation['name']}
            </p>
              <img src={image_url}
                   alt={image_alt}
                   width="100%" />

            </div>
    );
  }
}

ReactDOM.render(
  <Layout dataUrl={"/cluster/activity"} />,
  document.getElementById('root-activity')
);
