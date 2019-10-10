import React from 'react';
import ReactDOM from 'react-dom';

import {
  ClusterSchematic,
  Avatar
} from './clusterschematic.jsx'

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
            cpuHistory: [],
            cpuColourHistory: []
          };
        }),
      cpuHistoryMax: 50,
      dataUrl: props.dataUrl,
      serverUpdateInterval: 50,
      pending: [],
      running: [],
      defaultAvatarColour: "#e3e3e3",
      avatarColours: [
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
            info.cpuHistory.push(info.cpu)
            info.cpuColourHistory.push(info.job.colour)

            // limit length to this.state.cpuHistoryMax
            const start = info.cpuHistory.length - this.state
              .cpuHistoryMax;
            const end = info.cpuHistory.length;
            if (start >= 0) {
              info.cpuHistory = info.cpuHistory.slice(start, end);
              info.cpuColourHistory = info.cpuColourHistory.slice(start,
                end);
            }

            // set the default job attributes
            info.job = {
              colour: this.state.defaultAvatarColour
            };

            // update current CPU value
            info.cpu = result.cpu_usage[index]

            return info;
          });

          // duplicate job info on each core
          // data is duplicated to simplify logic, but
          // preferrably should be treated as immutable
          result.running.forEach((job) => {
            job['cores'].forEach((core) => {
              newNodeInfo[core]['job'] = job;
              // set the (avatar) colour for this job
              newNodeInfo[core]['job']['colour'] = this.state
                .avatarColours[job.avatar - 1];
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
          <div className="pane lhs">
              <ClusterSchematic info={this.state.nodeInfo} />
          </div>
          <SimulationList simulations={this.state.running} title="Running"/>
          <SimulationList simulations={this.state.pending} title="Waiting"/>
      </div>
    );
  }
}

function SimulationList(props) {
    const simulations = props.simulations.map((sim) => {
        return <SimulationView key={sim['id']} simulation={sim}/>;
    });
    return (
        <div className="pane rhs">
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

    const image_url = "simulations/" + sim_id +
      "/elmeroutput0001-velomagn.png";

    var progressBar = null;

    if ('progress' in simulation) {
      progressBar =
        <div className="progress-indicator-container">
                  <div className="progress-indicator" style={{width : simulation.progress + "%"}}/>
          </div>
    }
    return (
      <div className="simulation-view">
      <div className="simulation-heading">
          <Avatar whom={simulation.avatar} />
          <div className="right">
              <div className="sim-title"> {simulation['name']} </div>
              {progressBar}
          </div>
      </div>
      <div className="simulation-data">
          <img src={image_url} />
      </div>
            </div>
    );
  }
}

ReactDOM.render(
  <Layout dataUrl={"/cluster/activity"} />,
  document.getElementById('root-activity')
);
