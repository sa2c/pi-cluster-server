import React from 'react';
import ReactDOM from 'react-dom';

import ClusterSchematic from './clusterschematic.jsx'

import css from '../assets/styles/activity.sass'

class Layout extends React.Component {
  constructor(props) {
    super(props);

    const cores = 16;

    this.state = {
      nodeInfo: Array(cores)
        .fill(0)
        .map((v) => {
          return {
            job: {},
            cpu: 0,
            cpuHistory: []
          };
        }),
      cpuHistoryMax: 10,
      dataUrl: props.dataUrl,
      serverUpdateInterval: 5000,
      pending: [],
      running: [],
      defaultAvatarColour: "#e3e3e3",
      avatarColours: [
        "#f26a44",
        "#3f3d31",
        "#d3ce3e",
        "#2eaeb7",
        "#fedb7d",
        "#2earb7",
        "#2eaeb7",
        "#fedb7d",
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
      ],
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
          var newNodeInfo = this.state.nodeInfo.map((info, index) => {
            // add previous value of CPU to cpuHistory
            info['cpuHistory'].push(info['cpu'])

            // limit length to this.state.cpuHistoryMax
            const start = info.cpuHistory.length - this.state
              .cpuHistoryMax;
            const end = info.cpuHistory.length;
            info.cpuHistory = info.cpuHistory.slice(start, end);

            // set the default job attributes
            info['job'] =  { colour : this.state.defaultAvatarColour };

            // update current CPU value
            info['cpu'] = result['cpu_usage'][index]

            return info;
          });

          // duplicate job info on each core
          // data is duplicated to simplify logic, but
          // preferrably should be treated as immutable
          result.running.forEach((job) => {
            job['cores'].forEach((core) => {
              newNodeInfo[core]['job'] = job;
              // set the (avatar) colour for this job
              newNodeInfo[core]['job']['colour'] = this.state.avatarColours[job.avatar - 1];
            });
          });

          this.setState({
            nodeInfo: newNodeInfo,
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
            <ClusterSchematic info={this.state.nodeInfo} />
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
